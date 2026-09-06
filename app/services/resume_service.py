import hashlib
import io
import re

import httpx
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.resume import Resume


def _google_drive_download_url(url: str) -> str | None:
    match = re.search(r"/file/d/([^/]+)", url)

    if not match:
        return None

    file_id = match.group(1)

    return f"https://drive.google.com/uc?export=download&id={file_id}"


def download_resume(url: str) -> bytes:
    download_url = _google_drive_download_url(url)

    if download_url:
        url = download_url

    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=30.0,
    )

    response.raise_for_status()

    content = response.content

    # Fail early with a useful error instead of giving
    # an obscure pypdf error.
    if not content.startswith(b"%PDF"):
        raise ValueError(
            f"Downloaded content is not a PDF. "
            f"Content-Type: {response.headers.get('content-type')}"
        )

    return content


def download_and_extract_resume(url: str) -> tuple[str, str]:
    content = download_resume(url)

    content_hash = hashlib.sha256(content).hexdigest()

    reader = PdfReader(io.BytesIO(content))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    extracted_text = "\n".join(pages).strip()

    return extracted_text, content_hash


def process_candidate_resume(
    candidate: Candidate,
    db: Session) -> Resume:

    existing = (
        db.query(Resume)
        .filter(Resume.candidate_id == candidate.id)
        .first()
    )

    if not candidate.resume_link:
        if existing:
            existing.status = "missing_url"
            db.commit()
            return existing

        resume = Resume(
            candidate_id=candidate.id,
            status="missing_url",
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return resume

    try:
        extracted_text, content_hash = download_and_extract_resume(
            candidate.resume_link
        )

        # Cache hit: resume content hasn't changed.
        if (
            existing
            and existing.content_hash == content_hash
            and existing.extracted_text
        ):
            return existing

        if existing:
            existing.source_url = candidate.resume_link
            existing.extracted_text = extracted_text
            existing.content_hash = content_hash
            existing.status = "processed"

            db.commit()
            db.refresh(existing)

            return existing

        resume = Resume(
            candidate_id=candidate.id,
            source_url=candidate.resume_link,
            extracted_text=extracted_text,
            content_hash=content_hash,
            status="processed",
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return resume

    except Exception as exc:
        print(
            f"RESUME PROCESSING ERROR for candidate "
            f"{candidate.id}: {type(exc).__name__}: {exc}"
        )

        if existing:
            existing.status = "failed"
            db.commit()
            return existing

        resume = Resume(
            candidate_id=candidate.id,
            source_url=candidate.resume_link,
            status="failed",
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return resume