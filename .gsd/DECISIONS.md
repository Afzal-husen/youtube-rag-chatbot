# DECISIONS.md — Architecture Decision Record (ADR)

> **Status**: `ACTIVE`

## ADR-01: Backend Framework Selection
**Date**: 2026-04-13
**Status**: `ACCEPTED`
**Context**: We need a way to serve our RAG logic to a web frontend.
**Decision**: Use **FastAPI** instead of a simple CLI script.
**Rationale**: Native async support for LLM streaming, built-in OpenAPI docs, and clean Pydantic validation.

## ADR-02: Local Vector Store Persistence
**Date**: 2026-04-13
**Status**: `ACCEPTED`
**Context**: We want to avoid re-embedding videos we've already processed.
**Decision**: Use **FAISS `save_local()` / `load_local()`** with a file-based storage mapping.
**Rationale**: Simple, zero-cost, no extra infrastructure required for local dev.

## ADR-03: Frontend Technology
**Date**: 2026-04-13
**Status**: `ACCEPTED`
**Context**: We need a "premium" UI.
**Decision**: Use **Next.js (App Router)** with **Tailwind CSS**.
**Rationale**: Fastest development for high-quality, modern web apps.

## Phase 1 Decisions

**Date:** 2026-04-13

### Scope
- Full refactor of `main.py` into a modular `backend/` directory structure.
- Root `main.py` will be removed once the refactor is validated.

### Approach
- Chose: **Option A (Clean Slate Monorepo)**.
- Reason: Simplifies the project structure and avoids cluttering the root with legacy files.
- FAISS Naming: Use sanitized `video_id` as the directory name in `backend/storage/`.

### Constraints
- Acceptable to use `allow_dangerous_deserialization=True` for local FAISS loading as the environment is private and controlled.
- Storage path set to `backend/storage/`.
