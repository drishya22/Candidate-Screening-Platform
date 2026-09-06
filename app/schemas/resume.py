from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    candidate_id: int
    source_url: str | None = None
    extracted_text: str | None = None
    content_hash: str | None = None
    status: str

    model_config = {"from_attributes": True}