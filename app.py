from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router

app = FastAPI(title="AI PDF to CSV")
origins = [
    "http://localhost:5173",  # Typical Vite frontend port
    "http://localhost:3001",  # Typical React frontend port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows your specific frontends
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers (like Content-Type)
)
app.include_router(upload_router)
