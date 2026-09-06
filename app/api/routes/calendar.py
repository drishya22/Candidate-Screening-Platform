from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.services.calendar_service import (
    get_authorization_url,
    handle_oauth_callback,
    create_interview_event,
)


router = APIRouter(
    prefix="/api/calendar",
    tags=["Calendar"],
)


@router.get("/oauth/start")
def start_google_oauth():
    return {
        "authorization_url": get_authorization_url()
    }


@router.get("/oauth/callback")
def google_oauth_callback(code: str):
    try:
        handle_oauth_callback(code)

        return {
            "status": "connected",
            "message": "Google Calendar connected successfully.",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Google OAuth failed: {exc}",
        )


@router.post("/schedule")
def schedule_interview(
    candidate_name: str,
    candidate_email: str,
    start_time: datetime,
    end_time: datetime,
):
    try:
        return create_interview_event(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            start_time=start_time,
            end_time=end_time,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Interview scheduling failed: {exc}",
        )