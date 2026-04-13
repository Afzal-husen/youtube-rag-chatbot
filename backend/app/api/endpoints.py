import traceback
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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
    video_id = ingestion_mgr.extract_video_id(request.url)
    
    if vector_mgr.index_exists(video_id):
        metadata = ingestion_mgr.get_video_metadata(request.url)
        return ProcessUrlResponse(
            video_id=video_id,
            title=metadata.get("title", f"Video {video_id}"),
            author=metadata.get("author", "YouTube Content"),
            thumbnail_url=metadata.get("thumbnail_url"),
            already_indexed=True,
            message="Video already indexed. Loaded from local storage."
        )
    
    try:
        chunks = ingestion_mgr.load_and_split(request.url)
        vector_mgr.create_and_save_index(video_id, chunks)
        metadata = ingestion_mgr.get_video_metadata(request.url)
        
        return ProcessUrlResponse(
            video_id=video_id,
            title=metadata.get("title", f"Video {video_id}"),
            author=metadata.get("author", "YouTube Content"),
            already_indexed=False,
            message="Video indexed successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not vector_mgr.index_exists(request.video_id):
        raise HTTPException(status_code=404, detail="Video not indexed.")
    
    try:
        vector_store = vector_mgr.load_index(request.video_id)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        chain = rag_mgr.get_chain(retriever, model_name=request.model_name)
        
        # Invoke the chain (synchronous/async wrapper)
        result = await chain.ainvoke(request.question)
        
        sources = [
            {"content": doc.page_content, "metadata": doc.metadata} 
            for doc in result["docs"]
        ]
        
        return ChatResponse(
            answer=result["answer"],
            source_documents=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    if not vector_mgr.index_exists(request.video_id):
        raise HTTPException(status_code=404, detail="Video not indexed.")

    async def event_generator():
        try:
            vector_store = vector_mgr.load_index(request.video_id)
            retriever = vector_store.as_retriever(search_kwargs={"k": 4})
            chain = rag_mgr.get_chain(retriever, model_name=request.model_name)

            # First, send the sources
            source_docs = await retriever.ainvoke(request.question)
            sources = [
                {"content": doc.page_content, "metadata": doc.metadata} 
                for doc in source_docs
            ]
            yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"

            # Then, stream the answer
            # We use the specific 'answer' part of our parallel chain if we want to stream just that
            # However, for pure streaming of just the answer part of LCEL dict:
            async for chunk in chain.astream(request.question):
                if "answer" in chunk:
                    yield f"data: {json.dumps({'type': 'chunk', 'data': chunk['answer']})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
