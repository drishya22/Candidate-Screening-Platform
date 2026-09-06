from fastapi import APIRouter, Depends,File,HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.candidate_service import import_candidates

router=APIRouter(
    prefix="/api/candidates",
    tags=["Candidates"]
)

@router.post("/upload")
def upload_candidates(
    file: UploadFile=File(...),
    db:Session=Depends(get_db)
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
        result=import_candidates(file.file,db,file.filename)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to import candidate data:{exc}"
        )
