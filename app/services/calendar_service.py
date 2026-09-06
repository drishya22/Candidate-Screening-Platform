import os
import uuid
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]

CLIENT_SECRETS_FILE = os.getenv(
    "GOOGLE_CLIENT_SECRETS_FILE",
    "credentials/google_client_secret.json",
)

TOKEN_FILE = os.getenv(
    "GOOGLE_TOKEN_FILE",
    "token.json",
)

REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/api/calendar/oauth/callback",
)

CALENDAR_TIMEZONE = os.getenv(
    "CALENDAR_TIMEZONE",
    "Asia/Kolkata",
)


def get_authorization_url():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    # Preserve the PKCE verifier for the callback request.
    with open("oauth_code_verifier.txt", "w") as f:
        f.write(flow.code_verifier)

    return authorization_url


def handle_oauth_callback(code):
    if not os.path.exists("oauth_code_verifier.txt"):
        raise RuntimeError("OAuth code verifier is missing. Please start OAuth again.")

    with open("oauth_code_verifier.txt", "r") as f:
        code_verifier = f.read().strip()

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    # Restore the verifier generated during /oauth/start.
    flow.code_verifier = code_verifier

    flow.fetch_token(code=code)

    credentials = flow.credentials

    with open(TOKEN_FILE, "w") as token:
        token.write(credentials.to_json())

    # No longer needed after successful OAuth.
    try:
        os.remove("oauth_code_verifier.txt")
    except OSError:
        pass

    return credentials


def get_calendar_service():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())

    if not credentials or not credentials.valid:
        raise RuntimeError(
            "Google Calendar is not connected."
        )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
    )


def create_interview_event(
    candidate_name: str,
    candidate_email: str,
    start_time: datetime,
    end_time: datetime,
):
    service = get_calendar_service()

    event = {
        "summary": f"Interview - {candidate_name}",
        "description": (
            "Interview scheduled by Candidate Screening Platform."
        ),
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": CALENDAR_TIMEZONE,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": CALENDAR_TIMEZONE,
        },
        "attendees": [
            {
                "email": candidate_email,
            }
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {
                    "type": "hangoutsMeet"
                },
            }
        },
    }

    created_event = (
        service.events()
        .insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1,
            sendUpdates="all",
        )
        .execute()
    )

    meet_link = None

    conference_data = created_event.get(
        "conferenceData",
        {},
    )

    for entry_point in conference_data.get(
        "entryPoints",
        [],
    ):
        if entry_point.get("entryPointType") == "video":
            meet_link = entry_point.get("uri")
            break

    return {
        "event_id": created_event.get("id"),
        "event_link": created_event.get("htmlLink"),
        "meet_link": meet_link,
    }