# ROADMAP.md — YouTube RAG Insights Tool

> **Current Phase**: Phase 1: Foundation & Refactoring
> **Milestone**: v1.0 (Local-First MVP)

## Must-Haves (from SPEC)
- [ ] Paste URL and process video metadata.
- [ ] Persistent local FAISS disk index.
- [ ] Single-video chat interface (Groq-powered).
- [ ] High-end Next.js dashboard UI.

## Phases

### Phase 1: Foundation & Backend Refactoring
**Status**: ⬜ Not Started
**Objective**: Transition from script to a modular FastAPI backend with local disk storage.
**Requirements**: F-02, F-03, F-06, T-02, T-03, T-05

### Phase 2: Frontend Scaffolding & Design
**Status**: ⬜ Not Started
**Objective**: Initialize Next.js app with a premium UI shell (Tailwind/Shadcn).
**Requirements**: F-01, T-01, U-01, U-02

### Phase 3: Integration & Vector Processing
**Status**: ⬜ Not Started
**Objective**: Connect Frontend to Backend for URL submission and processing.
**Requirements**: F-01, F-02, F-05, U-03

### Phase 4: Chat Interface & Streaming
**Status**: ⬜ Not Started
**Objective**: Implement the RAG chat loop with SSE streaming.
**Requirements**: F-04, F-07, T-04, U-04, U-05

### Phase 5: Polish & Persistence
**Status**: ⬜ Not Started
**Objective**: Robustify the local storage, handle errors gracefully, and finalize the dashboard.
**Requirements**: F-03, F-06, U-05
