import traceback
import json
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.api.models import ProcessUrlRequest, ProcessUrlResponse, ChatRequest, ChatResponse
from app.core.ingestion import IngestionManager
from app.core.vector_store import VectorStoreManager
from app.core.rag_chain import RAGChainManager
from app.core.database import get_db
from app.core.db_models import VideoSession, ChatMessage

router = APIRouter()
ingestion_mgr = IngestionManager()
vector_mgr = VectorStoreManager()
rag_mgr = RAGChainManager()

@router.post("/process-url", response_model=ProcessUrlResponse)
async def process_url(request: ProcessUrlRequest, db: AsyncSession = Depends(get_db)):
    video_id = ingestion_mgr.extract_video_id(request.url)
    
    # Check if session exists in DB
    result = await db.execute(select(VideoSession).where(VideoSession.video_id == video_id))
    db_session = result.scalar_one_or_none()
    
    if db_session:
        return ProcessUrlResponse(
            video_id=video_id,
            title=db_session.custom_name or db_session.youtube_title,
            author=db_session.author or "YouTube Content",
            thumbnail_url=db_session.thumbnail_url,
            already_indexed=True,
            message="Video already indexed. Loaded from history."
        )
    
    try:
        chunks = ingestion_mgr.load_and_split(request.url)
        vector_mgr.create_and_save_index(video_id, chunks)
        metadata = ingestion_mgr.get_video_metadata(request.url)
        
        # Generate AI Title
        ai_title = await rag_mgr.generate_title(chunks)
        
        # Save to DB
        new_session = VideoSession(
            video_id=video_id,
            youtube_title=metadata.get("title", f"Video {video_id}"),
            custom_name=ai_title,
            author=metadata.get("author", "YouTube Content"),
            thumbnail_url=metadata.get("thumbnail_url")
        )
        db.add(new_session)
        await db.commit()
        
        return ProcessUrlResponse(
            video_id=video_id,
            title=ai_title,
            author=new_session.author,
            already_indexed=False,
            message="Video indexed and session saved."
        )
    except Exception as e:
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not vector_mgr.index_exists(request.video_id):
        raise HTTPException(status_code=404, detail="Video not indexed.")
    
    try:
        vector_store = vector_mgr.load_index(request.video_id)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        chain = rag_mgr.get_chain(retriever, model_name=request.model_name)
        
        result = await chain.ainvoke(request.question)
        
        sources = [
            {"content": doc.page_content, "metadata": doc.metadata} 
            for doc in result["docs"]
        ]
        
        # Persist messages
        user_msg = ChatMessage(video_id=request.video_id, role="user", content=request.question)
        ai_msg = ChatMessage(video_id=request.video_id, role="assistant", content=result["answer"], sources=sources)
        db.add_all([user_msg, ai_msg])
        await db.commit()
        
        return ChatResponse(
            answer=result["answer"],
            source_documents=sources
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-stream")
async def chat_stream(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not vector_mgr.index_exists(request.video_id):
        raise HTTPException(status_code=404, detail="Video not indexed.")

    async def event_generator():
        full_answer = ""
        sources = []
        try:
            vector_store = vector_mgr.load_index(request.video_id)
            retriever = vector_store.as_retriever(search_kwargs={"k": 4})
            chain = rag_mgr.get_chain(retriever, model_name=request.model_name)

            # Sources first
            source_docs = await retriever.ainvoke(request.question)
            sources = [
                {"content": doc.page_content, "metadata": doc.metadata} 
                for doc in source_docs
            ]
            yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"

            # Stream answer
            async for chunk in chain.astream(request.question):
                if "answer" in chunk:
                    batch = chunk['answer']
                    full_answer += batch
                    yield f"data: {json.dumps({'type': 'chunk', 'data': batch})}\n\n"
            
            # Persist to DB once complete
            user_msg = ChatMessage(video_id=request.video_id, role="user", content=request.question)
            ai_msg = ChatMessage(video_id=request.video_id, role="assistant", content=full_answer, sources=sources)
            db.add_all([user_msg, ai_msg])
            await db.commit()
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            await db.rollback()
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/history")
async def get_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VideoSession).order_by(VideoSession.indexed_at.desc()))
    sessions = result.scalars().all()
    return sessions

@router.get("/history/{video_id}/messages")
async def get_session_messages(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatMessage).where(ChatMessage.video_id == video_id).order_by(ChatMessage.created_at.asc()))
    messages = result.scalars().all()
    return messages

@router.patch("/history/{video_id}")
async def rename_session(video_id: str, name: str, db: AsyncSession = Depends(get_db)):
    await db.execute(update(VideoSession).where(VideoSession.video_id == video_id).values(custom_name=name))
    await db.commit()
    return {"status": "success"}

@router.delete("/history/{video_id}")
async def delete_session(video_id: str, db: AsyncSession = Depends(get_db)):
    # Delete from DB
    await db.execute(delete(VideoSession).where(VideoSession.video_id == video_id))
    await db.commit()
    
    # Delete FAISS files
    vector_mgr.delete_index(video_id)
    return {"status": "success"}
