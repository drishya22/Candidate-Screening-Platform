import re
import logging

from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.candidate import Candidate
from app.models.evaluation import CandidateEvaluation
from app.models.job import Job
from app.models.resume import Resume
from app.services.ai_service import evaluate_candidate

logger = logging.getLogger(__name__)


STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "have",
    "will", "are", "you", "your", "our", "their", "into", "using",
    "use", "work", "working", "experience", "years", "year", "role",
    "candidate", "required", "requirements", "ability", "strong",
    "good", "knowledge", "skills", "skill", "looking", "must",
    "should", "would", "about", "based", "through", "including",
    "build", "building", "develop", "development", "responsible",
}


def _extract_terms(text: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b", text.lower())

    return {
        word.strip(".-+#")
        for word in words
        if word not in STOPWORDS
    }


def _heuristic_fallback(
    job_description: str,
    resume_text: str,
) -> dict:
    """
    Deterministic fallback used only when both LLM providers fail.

    Produces a candidate-specific score between 40 and 60
    based on JD/resume evidence overlap.

    This is NOT presented as an AI-generated score.
    """

    jd_terms = _extract_terms(job_description)
    resume_terms = _extract_terms(resume_text)

    if not jd_terms:
        score = 50.0
    else:
        matched_terms = jd_terms.intersection(resume_terms)
        coverage = len(matched_terms) / len(jd_terms)

        # Map evidence coverage into a conservative 40-60 range.
        score = 40.0 + min(20.0, coverage * 20.0)

    score = round(score, 1)

    return {
        "skills_score": score,
        "experience_score": score,
        "project_score": score,
        "education_score": score,
        "strengths": [
            "Resume contains evidence overlapping with the job description."
        ],
        "gaps": [
            "LLM-based evaluation was unavailable; heuristic fallback was used."
        ],
        "evidence": [
            {
                "requirement": "JD/resume relevance",
                "matched": score > 40,
                "evidence": (
                    "Deterministic lexical evidence match used as fallback."
                ),
            }
        ],
        "recommendation": "borderline",
    }


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

    try:
        # Primary + fallback LLM providers.
        result = evaluate_candidate(
            job_description=job.description,
            resume_text=resume.extracted_text,
        )

        logger.info(
            "LLM evaluation succeeded for candidate %s",
            candidate.id,
        )

    except Exception as exc:
        # Both LLM providers failed.
        logger.warning(
            "LLM evaluation unavailable for candidate %s. "
            "Using deterministic JD/resume fallback: %s",
            candidate.id,
            exc,
        )

        result = _heuristic_fallback(
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


def run_job_evaluation(job_id: int) -> None:

    db = SessionLocal()

    try:
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

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
                    f"AI evaluation completed for candidate {candidate.id}"
                )

            except Exception as exc:

                print(
                    f"AI EVALUATION ERROR for candidate {candidate.id}: "
                    f"{type(exc).__name__}: {exc}"
                )

    finally:
        db.close()