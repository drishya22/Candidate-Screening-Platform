from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        unique=True,
        index=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )

    