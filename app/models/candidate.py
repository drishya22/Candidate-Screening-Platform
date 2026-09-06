from sqlalchemy import Float,String,Text
from sqlalchemy.orm import Mapped,mapped_column

from app.models.database import Base

class Candidate(Base):
    __tablename__="candidates"
    id: Mapped[int]=mapped_column(primary_key=True,index=True)
    name: Mapped[str]=mapped_column(String(255))
    
    email: Mapped[str]=mapped_column(String(255),index=True)
    college: Mapped[str | None]=mapped_column(String(255),nullable=True)
    
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)

    best_ai_project: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_work: Mapped[str | None] = mapped_column(Text, nullable=True)

    github_profile: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resume_link: Mapped[str | None] = mapped_column(String(1000), nullable=True)    
