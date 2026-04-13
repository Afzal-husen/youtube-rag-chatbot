import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

# Set HuggingFace cache folder if not set
if "HF_HOME" not in os.environ:
    os.environ["HF_HOME"] = "D:/huggingface_cache"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables
    await init_db()
    yield

app = FastAPI(
    title="YouTube RAG Insights API",
    description="Backend API for interacting with YouTube transcripts using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to YouTube RAG Insights API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
