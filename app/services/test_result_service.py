import pandas as pd
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.test_result import TestResult


REQUIRED_COLUMNS = {
    "email",
    "test_la",
    "test_code",
}


def import_test_results(
    file,
    db: Session,
    filename: str,
) -> dict:

    if filename.lower().endswith(".xlsx"):
        dataframe = pd.read_excel(
            file,
            sheet_name="Test Result",
        )
    else:
        dataframe = pd.read_csv(file)

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

    created = 0
    updated = 0
    skipped = 0

    for _, row in dataframe.iterrows():

        email = _clean_value(row["email"])

        if not email:
            skipped += 1
            continue


        candidate = None

        # 1. Exact email match
        if email:
            candidate = (
                db.query(Candidate)
                .filter(Candidate.email == email)
                .first()
            )

        # 2. Fallback: name + college
        if not candidate:
            name = _clean_value(row["name"])
            college = _clean_value(row["college"])

            query = db.query(Candidate)

            if name:
                query = query.filter(Candidate.name == name)

            if college:
                query = query.filter(Candidate.college == college)

            candidate = query.first()

        # 3. No reliable match
        if not candidate:
            skipped += 1
            continue

        test_la = _clean_float(row["test_la"])
        test_code = _clean_float(row["test_code"])

        existing = (
            db.query(TestResult)
            .filter(TestResult.candidate_id == candidate.id)
            .first()
        )

        if existing:
            existing.test_la = test_la
            existing.test_code = test_code
            updated += 1
        else:
            result = TestResult(
                candidate_id=candidate.id,
                test_la=test_la,
                test_code=test_code,
            )

            db.add(result)
            created += 1

    db.commit()

    return {
        "total_rows": len(dataframe),
        "created": created,
        "updated": updated,
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