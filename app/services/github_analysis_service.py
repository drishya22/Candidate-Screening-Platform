from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.github_analysis import GitHubAnalysis

from app.services.github_service import (
    analyze_github_profile,
    calculate_github_score,
)


def analyze_candidate_github(
    candidate: Candidate,
    db: Session,
) -> GitHubAnalysis:

    if not candidate.github_profile:
        raise ValueError(
            f"No GitHub profile for candidate {candidate.id}"
        )

    github_data = analyze_github_profile(
        candidate.github_profile
    )

    score_data = calculate_github_score(
        github_data
    )

    existing = (
        db.query(GitHubAnalysis)
        .filter(
            GitHubAnalysis.candidate_id == candidate.id
        )
        .first()
    )

    if existing:
        analysis = existing
    else:
        analysis = GitHubAnalysis(
            candidate_id=candidate.id
        )
        db.add(analysis)

    analysis.score = score_data["score"]
    analysis.repository_relevance = score_data[
        "repository_relevance"
    ]
    analysis.engineering_signals = score_data[
        "engineering_signals"
    ]
    analysis.activity = score_data["activity"]
    analysis.documentation = score_data[
        "documentation"
    ]
    analysis.evidence = score_data["evidence"]
    analysis.repository_data = github_data["repositories"]

    db.commit()
    db.refresh(analysis)

    return analysis