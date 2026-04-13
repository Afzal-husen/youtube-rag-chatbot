from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProcessUrlRequest(BaseModel):
    url: str = Field(..., description="The YouTube video URL to process")

class ProcessUrlResponse(BaseModel):
    video_id: str
    title: str
    author: str
    thumbnail_url: Optional[str] = None
    already_indexed: bool
    message: str

class ChatRequest(BaseModel):
    video_id: str
    question: str
    model_name: Optional[str] = "llama-3.1-8b-instant"

class ChatResponse(BaseModel):
    answer: str
    source_documents: List[Dict[str, Any]]
