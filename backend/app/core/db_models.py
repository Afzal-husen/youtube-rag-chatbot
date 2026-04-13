from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class VideoSession(Base):
    __tablename__ = "video_sessions"

    video_id = Column(String, primary_key=True)
    custom_name = Column(String, nullable=True)
    youtube_title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    indexed_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey("video_sessions.video_id"), nullable=False)
    role = Column(String, nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("VideoSession", back_populates="messages")
