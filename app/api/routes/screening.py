from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.models.database import get_db, SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.github_analysis_service import analyze_candidate_github
from app.services.ranking_service import rank_candidates
from app.services.evaluation_service import run_job_evaluation
from app.services.resume_service import process_candidate_resume


router = APIRouter(
    prefix="/api/screening",
    tags=["Screening"],
)


_pipeline_state = {}
_pipeline_lock = Lock()


def _set_state(job_id: int, **values):
    with _pipeline_lock:
        state = _pipeline_state.setdefault(job_id, {})
        state.update(values)


def _github_worker(candidate_ids: list[int]):
    db = SessionLocal()
    results = []
    try:
        for candidate_id in candidate_ids:
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate:
                continue
            try:
                analysis = analyze_candidate_github(candidate, db)
                results.append({"candidate_id": candidate_id, "status": "analyzed", "score": analysis.score})
            except Exception as exc:
                results.append({"candidate_id": candidate_id, "status": "failed", "error": str(exc)})
        return results
    finally:
        db.close()


def _run_screening_pipeline(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            _set_state(job_id, status="failed", message="Job not found")
            return

        candidates = db.query(Candidate).all()
        if not candidates:
            _set_state(job_id, status="failed", message="No candidates uploaded")
            return

        _set_state(
            job_id,
            status="processing_resumes",
            message=f"Processing {len(candidates)} resumes...",
            total_candidates=len(candidates),
        )

        resume_results = []
        for candidate in candidates:
            try:
                resume = process_candidate_resume(candidate, db)
                resume_results.append({"candidate_id": candidate.id, "status": resume.status})
            except Exception as exc:
                resume_results.append({"candidate_id": candidate.id, "status": "failed", "error": str(exc)})

        candidate_ids = [c.id for c in candidates]
        _set_state(
            job_id,
            status="evaluating",
            message="Resumes processed. AI evaluation and repository analysis are running in parallel...",
            resume_results=resume_results,
        )
    finally:
        db.close()

    # These jobs use independent database sessions and can run concurrently.
    with ThreadPoolExecutor(max_workers=2) as executor:
        ai_future = executor.submit(run_job_evaluation, job_id)
        github_future = executor.submit(_github_worker, candidate_ids)

        try:
            ai_future.result()
            ai_status = "completed"
        except Exception as exc:
            ai_status = f"failed: {exc}"

        try:
            github_results = github_future.result()
        except Exception as exc:
            github_results = []
            _set_state(job_id, github_error=str(exc))

    db = SessionLocal()
    try:
        rankings = rank_candidates(job_id, db)
    finally:
        db.close()

    _set_state(
        job_id,
        status="completed",
        message=f"Screening completed. {len(rankings)} candidates ranked.",
        rankings=rankings,
        ai_status=ai_status,
        github_results=github_results,
    )


@router.post("/run/{job_id}")
def run_screening(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = db.query(Candidate).all()
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates uploaded")

    with _pipeline_lock:
        current = _pipeline_state.get(job_id, {})
        if current.get("status") in {"processing_resumes", "evaluating"}:
            return {"job_id": job_id, "status": "already_running", "message": current.get("message")}
        _pipeline_state[job_id] = {
            "status": "queued",
            "message": "Screening pipeline queued.",
            "total_candidates": len(candidates),
        }

    background_tasks.add_task(_run_screening_pipeline, job_id)

    return {
        "job_id": job_id,
        "status": "queued",
        "total_candidates": len(candidates),
        "message": "Screening started. Resume processing will run first, followed by parallel AI and GitHub analysis.",
    }


@router.get("/run/{job_id}/status")
def screening_status(job_id: int):
    state = _pipeline_state.get(job_id)
    if not state:
        return {
            "job_id": job_id,
            "status": "idle",
            "message": "No screening run has been started for this job.",
        }
    return {"job_id": job_id, **state}


@router.post("/github")
def analyze_github(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    results = []

    for candidate in candidates:
        try:
            analysis = analyze_candidate_github(candidate, db)
            results.append({
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "status": "analyzed",
                "github_score": analysis.score,
            })
        except Exception as exc:
            results.append({
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "status": "failed",
                "error": str(exc),
            })

    return {"total_candidates": len(candidates), "results": results}


@router.get("/ranking/{job_id}")
def get_ranking(job_id: int, db: Session = Depends(get_db)):
    return {
        "job_id": job_id,
        "rankings": rank_candidates(job_id, db),
    }
