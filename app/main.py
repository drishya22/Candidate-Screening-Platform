from fastapi import FastAPI 
from app.models.database import Base,engine
from app.models.candidate import Candidate
from app.api.routes.candidate import router as candidate_router
from app.api.routes.test_result import router as test_result_router
from app.models.test_result import TestResult
from app.models.job import Job
from app.models.resume import Resume
from app.models.evaluation import CandidateEvaluation
from app.models.github_analysis import GitHubAnalysis
from app.api.routes.jobs import router as jobs_router
from app.api.routes.calendar import router as calendar_router
from app.api.routes.screening import router as screening_router


Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="Candidate Screening Platform",
    version="0.1.0"
)

app.include_router(candidate_router)
app.include_router(test_result_router)
app.include_router(jobs_router)
app.include_router(screening_router)
app.include_router(calendar_router)

@app.get("/health")
def health_check():
    return {"status":"healthy"}


