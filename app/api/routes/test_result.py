from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.test_result_service import import_test_results


router = APIRouter(
    prefix="/api/test-results",
    tags=["Test Results"],
)


@router.post("/upload")
def upload_test_results(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    filename = file.filename.lower()

    if not filename.endswith((".csv", ".xlsx")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported.",
        )

    try:
        result = import_test_results(
            file.file,
            db,
            file.filename,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to import test results: {exc}",
        )