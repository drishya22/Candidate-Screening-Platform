from pydantic import BaseModel

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    college: str | None=None
    branch: str | None=None
    cgpa: float | None=None
    best_ai_project: str | None=None
    research_work: str| None=None
    github_profile: str | None=None
    resume_link: str | None=None

    model_config={"from_attributes":True}