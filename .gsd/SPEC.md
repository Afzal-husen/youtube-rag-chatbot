# SPEC.md — YouTube RAG Insights Tool

> **Status**: `FINALIZED`

## Vision
A premium, private web application that transforms collective YouTube video knowledge into an interactive expert. Users paste a video URL and immediately gain a high-speed, Groq-powered chat interface that answers questions based on that specific video's content with high accuracy and minimal latency.

## Goals
1. **Dynamic Video Indexing:** Allow users to fetch and process ANY public YouTube video transcript via a Next.js interface.
2. **Persistent Local Memory:** Store vector embeddings in a disk-based FAISS index to avoid re-calculating for previously watched videos.
3. **High-Value UI:** Deliver a premium "SaaS-like" dashboard with a clear chat interface, video metadata (title, channel), and message history.
4. **Architectural Decoupling:** Build with a clean FastAPI backend so switching from local FAISS to cloud Pinecone/Supabase is a configuration change.

## Non-Goals (Out of Scope)
- **Multi-Video Queries:** Chatting across a cluster of videos (V1 focus is single-video deep dives).
- **Public User Accounts:** No multi-tenant auth or database-backed user management for this initial private version.
- **Advanced Video Analytics:** No sentiment analysis or frame-based RAG for now; text-only transcripts.

## Users
Professional learners and creators who need to quickly extract specific information from long-form YouTube tutorials or interviews.

## Constraints
- **Local FAISS:** Memory/Disk usage must be managed for local storage.
- **Groq API Limits:** Reliability depends on Groq's throughput and usage tiers.
- **YouTube API Changes:** Dependent on the `youtube-transcript-api` staying functional with current YouTube scrapers.

## Success Criteria
- [ ] Users can paste a URL and see a "Success" message within 15 seconds.
- [ ] Chat responses consistently cite context from the transcript.
- [ ] Previously indexed videos load "instantly" from the local FAISS disk index.
- [ ] The UI feels premium, responsive, and "alive" with modern animations.
