# REQUIREMENTS.md — YouTube RAG Insights Tool

> **Status**: `DRAFT`
> **Date**: 2026-04-13

## Functional Requirements
| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **F-01** | Support YouTube URL input via a Next.js interface. | SPEC Goal 1 | Pending |
| **F-02** | Fetch and process transcripts (chunking, embeddings) from YouTube. | SPEC Goal 1 | Pending |
| **F-03** | Persistent local FAISS disk index per video ID. | SPEC Goal 2 | Pending |
| **F-04** | "Chat" interface with a video for RAG-based Q&A. | SPEC Goal 1 | Pending |
| **F-05** | Load video metadata (title, author, thumbnail) for the UI. | SPEC Goal 3 | Pending |
| **F-06** | Check for local index existence before re-processing (instant loading). | SPEC Goal 2 | Pending |
| **F-07** | Streaming LLM responses (SSE) from FastAPI to Next.js. | SPEC Goal 3 | Pending |

## Technical Requirements
| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **T-01** | Next.js (App Router) for frontend. | RESEARCH 1 | Pending |
| **T-02** | FastAPI for backend API. | RESEARCH 1 | Pending |
| **T-03** | LangChain for RAG orchestration. | RESEARCH 4 | Pending |
| **T-04** | Groq API for Llama3 inference. | RESEARCH 4 | Pending |
| **T-05** | FAISS `save_local()` / `load_local()` for disk persistence. | RESEARCH 2 | Pending |
| **T-06** | HuggingFace `sentence-transformers` for local embeddings. | RESEARCH 5 | Pending |

## UI/UX Requirements
| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| **U-01** | Dark/Light mode support (preferred Dark). | SPEC Vision | Pending |
| **U-02** | "Glassmorphism" or high-end dashboard aesthetics. | SPEC Goal 3 | Pending |
| **U-03** | Loading states for ingestion and processing. | SPEC Goal 3 | Pending |
| **U-04** | Responsive chat bubbles and message history. | SPEC Goal 3 | Pending |
| **U-05** | Sidebar for previously indexed videos (Session based or folder based). | SPEC Goal 3 | Pending |
