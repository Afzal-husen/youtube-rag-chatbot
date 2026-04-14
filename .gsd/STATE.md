# Project State

## Current Position
- **Phase**: Phase 4/5 Transitional (RAG Fix & UX Polish)
- **Task**: Post-Implementation Handoff
- **Status**: Paused at 2026-04-14 10:07 IST

## Last Session Summary
Resolved critical RAG response failure by implementing "Dense Chunking" logic in `ingestion.py`. Fixed several UI/UX issues related to chat scrolling and input interaction. Optimized backend startup performance and resolved a persistent "dirty submodule" issue with the `frontend` directory.

## In-Progress Work
- Ready for Phase 5 (Deployment & Production Polish).
- All fixes committed to `main` branch.
- Files modified: `backend/app/api/endpoints.py`, `backend/app/core/ingestion.py`, `backend/app/core/rag_chain.py`, `backend/app/core/vector_store.py`, `backend/app/main.py`, `frontend/src/app/page.tsx`, `frontend/src/components/chat-interface.tsx`.

## Blockers
- None.

## Context Dump
### Decisions Made
- **Dense Windowing**: Switched from segment-based indexing to 1000-character overlapping windows (0.15 ratio) to provide the LLM with sufficient context.
- **Lazy Loading**: Implemented lazy property for `HuggingFaceEmbeddings` to reduce server start time from 60s to <1s.
- **Submodule Removal**: Converted the `frontend` submodule into a standard directory to simplify single-repo management.
- **Pointer-Events-None**: Added to decorative UI layers to prevent them from blocking clicks to input fields.

### Approaches Tried
- **Attribute vs Dict Access**: Verified that the local `YouTubeTranscriptApi` version returns objects, not dictionaries, in this environment.
- **Top-K Retrieval**: Increased `k` from 4 to 8 to improve answer quality for broad questions.

### Current Hypothesis
The "I don't know" responses were entirely caused by context starvation (30-word snippets). The current 1000-char chunks provide robust grounding for Llama-3-8B.

### Files of Interest
- `backend/app/core/ingestion.py`: Window-grouping logic.
- `backend/app/core/rag_chain.py`: Refined RAG prompt.
- `frontend/src/components/chat-interface.tsx`: Scrolling and input fixes.

## Next Steps
1. Push changes: `git push origin main`.
2. Start Phase 5 (Deployment & Polish).
3. Dockerization and Production documentation.
