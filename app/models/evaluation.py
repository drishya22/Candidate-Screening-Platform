from sqlalchemy import ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class CandidateEvaluation(Base):
    __tablename__ = "candidate_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        index=True,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        index=True,
    )

    skills_score: Mapped[int]
    experience_score: Mapped[int]
    project_score: Mapped[int]
    education_score: Mapped[int]

    strengths: Mapped[list] = mapped_column(JSON)
    gaps: Mapped[list] = mapped_column(JSON)
    evidence: Mapped[list] = mapped_column(JSON)

    recommendation: Mapped[str] = mapped_column(
        Text,
        index=True,
    )

    evaluator_version: Mapped[str] = mapped_column(
        Text,
        default="v1",
    )