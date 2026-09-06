from sqlalchemy import Text, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(255),
    )

    description: Mapped[str] = mapped_column(
        Text,
    )