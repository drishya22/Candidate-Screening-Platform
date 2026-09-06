from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.database import Base, engine

from app.api.routes.candidates import router as candidates_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.screening import router as screening_router
from app.api.routes.test_result import router as test_result_router
from app.api.routes.calendar import router as calendar_router


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Candidate Screening Platform",
    description="AI-powered candidate screening and recruitment automation platform",
    version="1.0.0",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# API ROUTES MUST BE REGISTERED BEFORE THE FRONTEND CATCH-ALL
# ------------------------------------------------------------------

app.include_router(candidates_router)
app.include_router(jobs_router)
app.include_router(screening_router)
app.include_router(test_result_router)
app.include_router(calendar_router)


# ------------------------------------------------------------------
# Frontend
# ------------------------------------------------------------------

app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend",
)