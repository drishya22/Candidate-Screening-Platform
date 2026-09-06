from fastapi import FastAPI 
from app.models.database import Base,engine
from app.models.candidate import Candidate
from app.api.routes.candidate import router as candidate_router

Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="Candidate Screening Platform",
    version="0.1.0"
)

app.include_router(candidate_router)

@app.get("/health")
def health_check():
    return {"status":"healthy"}


