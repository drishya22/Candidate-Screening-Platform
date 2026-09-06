from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse

from app.models.candidate import Candidate
from app.services.resume_service import process_candidate_resume

from app.services.evaluation_service import run_job_evaluation

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)


@router.post(
    "",
    response_model=JobResponse,
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
):
    job = Job(
        title=job_data.title,
        description=job_data.description,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job



@router.post("/{job_id}/process-resumes")
def process_resumes(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    candidates = db.query(Candidate).all()

    results = []

    for candidate in candidates:
        resume = process_candidate_resume(
            candidate,
            db,
        )

        results.append(
            {
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "status": resume.status,
                "resume_id": resume.id,
            }
        )

    return {
        "job_id": job_id,
        "total_candidates": len(candidates),
        "results": results,
    }    

@router.post("/{job_id}/evaluate")
def evaluate_job_candidates(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    candidates = db.query(Candidate).all()

    background_tasks.add_task(
        run_job_evaluation,
        job_id,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "total_candidates": len(candidates),
        "message": "AI evaluation started in the background.",
    }