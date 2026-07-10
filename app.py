from fastapi import FastAPI
from routes.upload import router as upload_router

app = FastAPI(title="AI PDF to CSV")

app.include_router(upload_router)
