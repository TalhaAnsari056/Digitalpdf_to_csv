from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config import OUTPUT_DIR

router = APIRouter(prefix="/download", tags=["Download"])


@router.get("/{document_name}/csv")
def download_csv(document_name: str):

    file_path = OUTPUT_DIR / document_name / "csv" / "output.csv"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="CSV file not found.")

    return FileResponse(
        path=file_path,
        filename="output.csv",
        media_type="text/csv",
    )


@router.get("/{document_name}/excel")
def download_excel(document_name: str):

    excel_folder = OUTPUT_DIR / document_name / "excel"

    files = list(excel_folder.glob("*.xlsx"))

    if not files:
        raise HTTPException(status_code=404, detail="Excel file not found.")

    file_path = files[0]

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
