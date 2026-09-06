from pydantic import BaseModel


class TestResultResponse(BaseModel):
    id: int
    candidate_id: int
    test_la: float | None = None
    test_code: float | None = None

    model_config = {"from_attributes": True}