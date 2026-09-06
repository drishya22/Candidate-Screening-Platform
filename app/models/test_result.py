from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        unique=True,
        index=True,
    )

    test_la: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    test_code: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )