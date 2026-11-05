# Luna - JUIT AI Assistant

Official senior AI assistant for Jaypee University of Information Technology (JUIT) Solan. Rebuilt for high-precision retrieval and modular scalability.

## Current Model (v2.0 Rebuild)

Luna operates on a **Dual-Track RAG (Retrieval-Augmented Generation)** architecture, ensuring 100% accuracy for official records while providing helpful context for general inquiries.

### Core Architecture
- **Language Model:** Ollama-hosted **Gemma 4 (e2b)** for senior-level reasoning and professional tone.
- **Track A+ (Official Records):**
    - **PostgreSQL:** High-precision database for faculty (100+ profiles) and administrative staff.
    - **Fact Registry:** Deterministic keyword-matching for fees, admissions, and rankings.
    - **Safety Valve:** Interactive "Did you mean...?" handling for misspelled names.
- **Track B (Website Knowledge):**
    - **Hybrid Search:** Combines **Vector Similarity (ChromaDB)** with **Keyword Search (BM25)**.
    - **Demotion Strategy:** Supplementary data is strictly filtered and marked with a confidence disclaimer.
- **Modular Backend:** FastAPI with asynchronous streaming and conversational memory buffers.

---

## Future Roadmap

### Phase 1: Quality & Observability
- **Synthetic Evaluation:** Implement RAGAS/TruLens to mathematically prove accuracy (Faithfulness & Relevance).
- **Tracing:** Integrate LangSmith/LangChain Tracing to monitor the "Inner Monologue" of the AI.
- **Telemetry:** Asynchronous query logging to identify "Knowledge Gaps" in the database.

### Phase 2: Maintenance & Performance
- **Automated Ingestion:** Cron-scheduled pipeline (`Crawl` -> `Parse` -> `Sync`) to keep the mirror and database updated.
- **Persistent Caching:** Disk-based caching for frequent queries to reduce LLM compute costs and latency.
- **Rate Limiting:** IP-based throttling to prevent resource exhaustion and abuse.

### Phase 3: UX & Interface
- **Deep Citations:** Moving from raw URLs to specific text-snippet highlighting.
- **UI Enhancements:** Thumb Up/Down feedback loop and visual trust indicators for different data sources.
- **Voice Integration:** Basic WebSpeech API support for hands-free campus inquiries.
