from fastapi import APIRouter, UploadFile, File, HTTPException
from agents.extraction_agent import ExtractionAgent
from agents.upload_agent import UploadAgent
from pipeline.processing_pipeline import ProcessingPipeline

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    saved_path = UploadAgent.save_pdf(file)
    document = ProcessingPipeline.run(saved_path)

    return {
        "message": "Processing Completed.",
        "pages": len(document.pages),
        "document_type": document.document_type,
    }
