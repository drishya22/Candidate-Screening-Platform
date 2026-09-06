from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.candidate import Candidate
from app.models.evaluation import CandidateEvaluation
from app.models.job import Job
from app.models.resume import Resume
from app.services.ai_service import evaluate_candidate


def evaluate_single_candidate(
    db: Session,
    candidate: Candidate,
    job: Job,
) -> CandidateEvaluation:

    resume = (
        db.query(Resume)
        .filter(Resume.candidate_id == candidate.id)
        .first()
    )

    if not resume or not resume.extracted_text:
        raise ValueError(
            f"No processed resume found for candidate {candidate.id}"
        )

    result = evaluate_candidate(
        job_description=job.description,
        resume_text=resume.extracted_text,
    )

    existing = (
        db.query(CandidateEvaluation)
        .filter(
            CandidateEvaluation.candidate_id == candidate.id,
            CandidateEvaluation.job_id == job.id,
        )
        .first()
    )

    if existing:
        evaluation = existing

        evaluation.skills_score = result["skills_score"]
        evaluation.experience_score = result["experience_score"]
        evaluation.project_score = result["project_score"]
        evaluation.education_score = result["education_score"]
        evaluation.strengths = result["strengths"]
        evaluation.gaps = result["gaps"]
        evaluation.evidence = result["evidence"]
        evaluation.recommendation = result["recommendation"]

    else:
        evaluation = CandidateEvaluation(
            candidate_id=candidate.id,
            job_id=job.id,
            skills_score=result["skills_score"],
            experience_score=result["experience_score"],
            project_score=result["project_score"],
            education_score=result["education_score"],
            strengths=result["strengths"],
            gaps=result["gaps"],
            evidence=result["evidence"],
            recommendation=result["recommendation"],
            evaluator_version="v1",
        )

        db.add(evaluation)

    db.commit()
    db.refresh(evaluation)

    return evaluation

from app.models.database import SessionLocal


def run_job_evaluation(job_id: int) -> None:
    db = SessionLocal()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            print(f"AI EVALUATION ERROR: Job {job_id} not found")
            return

        candidates = db.query(Candidate).all()

        for candidate in candidates:
            try:
                evaluate_single_candidate(
                    db=db,
                    candidate=candidate,
                    job=job,
                )

                print(
                    f"AI evaluation completed for candidate "
                    f"{candidate.id}"
                )

            except Exception as exc:
                print(
                    f"AI EVALUATION ERROR for candidate "
                    f"{candidate.id}: "
                    f"{type(exc).__name__}: {exc}"
                )

    finally:
        db.close()    