from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.evaluation import CandidateEvaluation
from app.models.github_analysis import GitHubAnalysis
from app.models.test_result import TestResult


def calculate_final_score(
    evaluation: CandidateEvaluation,
    github: GitHubAnalysis | None,
    test: TestResult | None,
) -> float:

    # AI/JD relevance
    ai_score = (
        evaluation.skills_score * 0.35
        + evaluation.experience_score * 0.20
        + evaluation.project_score * 0.30
        + evaluation.education_score * 0.15
    )

    github_score = github.score if github else 0.0

    if test:
        test_score = (
            test.test_la * 0.4
            + test.test_code * 0.6
        )
    else:
        test_score = 0.0

    # Overall candidate score
    final_score = (
        ai_score * 0.50
        + github_score * 0.20
        + test_score * 0.30
    )

    return round(final_score, 2)

def get_final_decision(final_score: float) -> str:
    if final_score >= 80:
        return "strong_shortlist"
    if final_score >= 65:
        return "shortlist"
    if final_score >= 50:
        return "borderline"
    return "reject"    


def rank_candidates(
    job_id: int,
    db: Session,
) -> list[dict]:

    candidates = db.query(Candidate).all()

    ranked = []

    for candidate in candidates:

        evaluation = (
            db.query(CandidateEvaluation)
            .filter(
                CandidateEvaluation.candidate_id == candidate.id,
                CandidateEvaluation.job_id == job_id,
            )
            .first()
        )

        if not evaluation:
            continue

        github = (
            db.query(GitHubAnalysis)
            .filter(
                GitHubAnalysis.candidate_id == candidate.id
            )
            .first()
        )

        test = (
            db.query(TestResult)
            .filter(
                TestResult.candidate_id == candidate.id
            )
            .first()
        )

        final_score = calculate_final_score(
            evaluation,
            github,
            test,
        )

        ranked.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "email": candidate.email,
            "ai_score": round(
                (
                    evaluation.skills_score * 0.35
                    + evaluation.experience_score * 0.20
                    + evaluation.project_score * 0.30
                    + evaluation.education_score * 0.15
                ),
                2,
            ),
            "github_score": (
                github.score if github else None
            ),
            "test_score": (
                round(
                    test.test_la * 0.4
                    + test.test_code * 0.6,
                    2,
                )
                if test
                else None
            ),
            "final_score": final_score,
            "recommendation": get_final_decision(final_score),
        })

    ranked.sort(
        key=lambda x: x["final_score"],
        reverse=True,
    )

    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank

    return ranked