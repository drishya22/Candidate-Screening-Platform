from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int

    skills_score: int
    experience_score: int
    project_score: int
    education_score: int

    strengths: list[str]
    gaps: list[str]
    evidence: list[dict]

    recommendation: str
    evaluator_version: str

    model_config = {"from_attributes": True}