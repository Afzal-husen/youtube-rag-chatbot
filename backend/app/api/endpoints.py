import traceback
from fastapi import APIRouter, HTTPException
from app.api.models import ProcessUrlRequest, ProcessUrlResponse, ChatRequest, ChatResponse
from app.core.ingestion import IngestionManager
from app.core.vector_store import VectorStoreManager
from app.core.rag_chain import RAGChainManager

router = APIRouter()
ingestion_mgr = IngestionManager()
vector_mgr = VectorStoreManager()
rag_mgr = RAGChainManager()

@router.post("/process-url", response_model=ProcessUrlResponse)
async def process_url(request: ProcessUrlRequest):
    print(f"Received request to process URL: {request.url}")
    video_id = ingestion_mgr.extract_video_id(request.url)
    print(f"Extracted video_id: {video_id}")
    
    if vector_mgr.index_exists(video_id):
        metadata = ingestion_mgr.get_video_metadata(request.url)
        return ProcessUrlResponse(
            video_id=video_id,
            title=metadata.get("title", "Unknown"),
            author=metadata.get("author", "Unknown"),
            thumbnail_url=metadata.get("thumbnail_url"),
            already_indexed=True,
            message="Video already indexed. Loaded from local storage."
        )
    
    try:
        # Load and split
        chunks = ingestion_mgr.load_and_split(request.url)
        # Create index
        vector_mgr.create_and_save_index(video_id, chunks)
        # Get metadata for response
        metadata = ingestion_mgr.get_video_metadata(request.url)
        
        return ProcessUrlResponse(
            video_id=video_id,
            title=metadata.get("title", "Unknown"),
            author=metadata.get("author", "Unknown"),
            thumbnail_url=metadata.get("thumbnail_url"),
            already_indexed=False,
            message="Video indexed successfully."
        )
    except Exception as e:
        error_detail = f"{str(e)}\n\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not vector_mgr.index_exists(request.video_id):
        raise HTTPException(status_code=404, detail="Video not indexed.")
    
    try:
        vector_store = vector_mgr.load_index(request.video_id)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        chain = rag_mgr.get_chain(retriever)
        
        # Simple invoke for now; streaming can be added later
        result = chain.invoke(request.question)
        
        # Get source documents for the citation requirement
        source_docs = retriever.invoke(request.question)
        sources = [
            {"content": doc.page_content, "metadata": doc.metadata} 
            for doc in source_docs
        ]
        
        return ChatResponse(
            answer=result,
            source_documents=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
