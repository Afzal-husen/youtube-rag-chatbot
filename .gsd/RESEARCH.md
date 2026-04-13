# RESEARCH.md — YouTube RAG Insights Tool

> **Status**: `COMPLETED`
> **Date**: 2026-04-13

## 1. Project Structure: Next.js + FastAPI
To maintain a high-quality developer experience and clear separation of concerns, we will use a subfolder-based monorepo structure.

```text
/
├── frontend/          # Next.js (App Router, Tailwind, Shadcn UI)
├── backend/           # FastAPI (Python, LangChain)
├── .venv/             # Shared Python virtual environment
├── .env               # Shared environment variables
└── README.md
```

**Rationale:**
- **FastAPI:** Superior for LLM tasks due to async support and native Pydantic validation.
- **Next.js:** Industry-standard for premium UIs.

## 2. FAISS Local Persistence
LangChain provides `save_local` and `load_local` methods for FAISS.

**Implementation Pattern:**
1. Generate `video_id` from URL.
2. Check if `backend/storage/faiss_{video_id}/` exists.
3. If yes, `FAISS.load_local(..., allow_dangerous_deserialization=True)`.
4. If no, fetch transcript, index, and `vectorstore.save_local(...)`.

**Risk:** Pickle safety. **Mitigation:** Since this is a private tool and we generate the indexes ourselves, `allow_dangerous_deserialization` is acceptable.

## 3. Metadata Extraction
We will use `langchain_community.document_loaders.YoutubeLoader` with `add_video_info=True`.

**Benefits:**
- Extracts Title, Author, Length, and Thumbnail.
- Simplifies the ingestion pipeline by wrapping `youtube-transcript-api`.

## 4. LLM & Connectivity
- **Model:** `llama3-70b-8192` (via Groq) for best balance of reasoning and speed.
- **Communication:** Frontend will communicate with Backend via standard REST API (`POST /process-url`, `POST /chat`).
- **Streaming:** Implement Server-Sent Events (SSE) from FastAPI to Next.js for a premium "typing" effect in chat.

## 5. Technology Choices (Summary)
| Layer | Tech | Rationale |
|-------|------|-----------|
| **Frontend** | Next.js 14+ | App router, performance, premium feel |
| **Styling** | Tailwind CSS | Rapid, consistent styling |
| **Backend** | FastAPI | High performance, async, Python-native |
| **RAG** | LangChain | Standard for LLM orchestration |
| **Embeddings**| HuggingFace | Free, local, high quality |
| **Vector DB** | FAISS | Fast, local-first, low overhead |
| **LLM** | Groq | Ultra-low latency inference |
