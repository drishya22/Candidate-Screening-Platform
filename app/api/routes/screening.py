from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.candidate import Candidate

from app.services.github_analysis_service import (
    analyze_candidate_github,
)
from app.services.ranking_service import rank_candidates


router = APIRouter(
    prefix="/api/screening",
    tags=["Screening"],
)


@router.post("/github")
def analyze_github(
    db: Session = Depends(get_db),
):
    candidates = db.query(Candidate).all()

    results = []

    for candidate in candidates:
        try:
            analysis = analyze_candidate_github(
                candidate,
                db,
            )

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

    return {
        "total_candidates": len(candidates),
        "results": results,
    }


@router.get("/ranking/{job_id}")
def get_ranking(
    job_id: int,
    db: Session = Depends(get_db),
):
    return {
        "job_id": job_id,
        "rankings": rank_candidates(
            job_id,
            db,
        ),
    }    