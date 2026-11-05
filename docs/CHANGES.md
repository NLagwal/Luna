# Project Changes & Roadmap

## Architectural Enhancements

### 1. Database-Driven Faculty Search
- **Implementation:** Transitioned from static JSON dictionaries to a robust PostgreSQL database for faculty profiles.
- **Logic:** Integrated `rapidfuzz` for high-precision name matching combined with LangChain for context-aware responses.
- **Status:** Integrated.

### 2. "Did you mean...?" Safety Valve (Ambiguity Handler)
- **Problem:** Users misspelling names often triggered a "Not Found" response or an irrelevant semantic search.
- **Solution:** Added a confidence threshold check (65% - 79%). If a query matches a faculty member within this range, Luna will proactively ask: *"I couldn't find a perfect match for '[Input]'. Did you mean Dr. [Closest Match]? If so, please ask specifically about them."*
- **Benefit:** Maintains 110% determinism while improving user experience.
- **Status:** Planned/Implementing.

### 3. Expanded "Fact Registry" (Track A+)
- **Problem:** Key administrative topics were handled by broad semantic searches, which can be inconsistent.
- **Solution:** Migrating the internal `fact_topics` dictionary to a dedicated `topics.json`. This registry is being expanded to include specific, official blocks for departments like:
    - Admissions
    - Placements
    - Account Office
- **Benefit:** Reduces LLM interpretation of raw website data by providing official structured facts for common administrative inquiries.
- **Status:** Integrated.

### 4. Abuse Prevention & Performance
- **Rate Limiting:** Implementation of IP-based throttling (using `slowapi`) to prevent resource exhaustion of the local Ollama/ChromaDB instances from automated abuse.
- **Persistent Caching:** Implementation of a disk-based response cache (using `diskcache`) to provide near-instant answers for repeated queries, significantly reducing latency and compute costs.
- **Input Guardrails:** Enforcement of strict query length constraints (e.g., 500 characters) and basic sanitization to protect against prompt injection and memory-intensive inputs.
- **Status:** Planned.

### 5. Conversational Memory (Context Awareness)
- **Goal:** Enable Luna to handle follow-up questions (e.g., "What are his research interests?") by maintaining a short-term history of the dialogue.
- **Implementation:** Session-based memory buffers integrated into the LangChain prompt.
- **Status:** Planned.

### 6. User Feedback & Analytics
- **Feedback Loop:** Adding Thumb Up/Down interaction to the UI to collect qualitative data on response accuracy.
- **Query Telemetry:** Implementing asynchronous logging of all user queries to identify "Knowledge Gaps" (topics requested by users that aren't yet in the database).
- **Status:** Planned.

### 7. UX & Transparency Enhancements
- **Deep Citations:** Improving the citation system to show the specific text snippet/context used for the answer, rather than just a raw URL/PDF link.
- **Source Trust Levels:** Visually distinguishing between "Official Records" (Track A) and "Website Knowledge" (Track B) in the chat interface.
- **Status:** Planned.

### 8. Automated Knowledge Maintenance
- **Scheduled Ingestion:** Automating the data pipeline (`parser` -> `build_db` -> `ingest`) via cron/scheduler to ensure the local mirror and vector store stay synchronized with the live university site.
- **Status:** Planned.

### 9. Vector DB "Demotion" Strategy (Precision Over Volume)
- **Goal:** Transform the Semantic Track (Track B) from a broad, "noisy" fallback into a high-precision supplementary tool.
- **Restrict the Scope:** Shift away from indexing the entire website. The vector database will only index a curated "Vault" of 10-20 critical documents (e.g., Prospectus, Fee Circulars, Academic Calendar).
- **Confidence Disclosure:** If an answer is derived from the Vector DB, Luna must prepend a mandatory disclaimer: *"Based on my search of university documents (which may be supplementary)..."*
- **Strict Similarity Filtering:** Implementation of a hard distance threshold in ChromaDB. If the retrieved context doesn't meet a high-relevance score, the system will fail gracefully rather than providing a "best-guess" answer.
- **Status:** Planned.

### 10. Performance-First AI Optimizations
- **Hybrid Search (BM25 + Vector):**
    - **Goal:** Improve retrieval precision for specific acronyms, room numbers, and department codes that vector search often misses.
    - **Implementation:** Combining semantic vector similarity with classic keyword-based matching (BM25) to provide a "best of both worlds" retrieval layer.
- **Early-Exit Intent Router:**
    - **Goal:** Drastically reduce latency and compute costs for simple or irrelevant queries.
    - **Implementation:** Using a lightweight, high-speed classifier to identify "Chitchat" or "Out of Scope" queries. These will receive instant pre-defined responses, bypassing the heavy RAG pipeline and saving LLM resources for complex questions.
- **Status:** Planned.

### 11. "God Tier" Quality Assurance & Observability
- **Automated RAG Evaluation (RAGAS/TruLens):**
    - **Goal:** Move from "it feels accurate" to "it is mathematically proven accurate."
    - **Implementation:** Developing a synthetic test suite to calculate metrics like Faithfulness, Answer Relevance, and Context Precision. This ensures that every code update improves—rather than degrades—Luna's performance.
- **Production Observability (LangSmith/Tracing):**
    - **Goal:** Gain full visibility into the "Inner Monologue" of the AI during live queries.
    - **Implementation:** Integrating tracing to monitor the exact flow of data between the Router, the DB, and the LLM. This allows for rapid debugging of "slow" queries and identifies exactly where a retrieval might have failed.
- **Status:** Planned.
