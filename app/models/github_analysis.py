from sqlalchemy import ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class GitHubAnalysis(Base):
    __tablename__ = "github_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        unique=True,
        index=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    repository_relevance: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    engineering_signals: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    activity: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    documentation: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    evidence: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    repository_data: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )