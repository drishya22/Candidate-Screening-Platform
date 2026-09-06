import pandas as pd
from sqlalchemy.orm import Session

from app.models.candidate import Candidate


REQUIRED_COLUMNS = {
    "name",
    "email",
    "college",
    "branch",
    "cgpa",
    "best_ai_project",
    "research_work",
    "github",
    "resume",
}


def import_candidates(file, db: Session, filename: str) -> dict:
    if filename.lower().endswith(".xlsx"):
        dataframe = pd.read_excel(file, sheet_name="Response")
    else:
        dataframe = pd.read_csv(file)

    # Normalize column names
    dataframe.columns = (
        dataframe.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    imported = 0
    skipped = 0

    for _, row in dataframe.iterrows():
        email = str(row["email"]).strip()

        if not email or email.lower() == "nan":
            skipped += 1
            continue

        existing = (
            db.query(Candidate)
            .filter(Candidate.email == email)
            .first()
        )

        if existing:
            skipped += 1
            continue

        candidate = Candidate(
            name=str(row["name"]).strip(),
            email=email,
            college=_clean_value(row["college"]),
            branch=_clean_value(row["branch"]),
            cgpa=_clean_float(row["cgpa"]),
            best_ai_project=_clean_value(row["best_ai_project"]),
            research_work=_clean_value(row["research_work"]),
            github_profile=_clean_value(row["github"]),
            resume_link=_clean_value(row["resume"]),
        )

        db.add(candidate)
        imported += 1

    db.commit()

    return {
        "total_rows": len(dataframe),
        "imported": imported,
        "skipped": skipped,
    }


def _clean_value(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    return value if value else None


def _clean_float(value):
    if pd.isna(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None