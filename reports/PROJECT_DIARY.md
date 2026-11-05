# Luna Project: 6-Week Engineering Diary & Progress Log

**Project Title:** Luna – Intelligent Retrieval-Augmented Campus Assistant  
**Institution:** Jaypee University of Information Technology (JUIT), Waknaghat  
**Supervisor:** Prof. Pradeep Kumar Gupta  
**Timeline:** Mid-June 2026 – Early August 2026  

---

### Team Roles & Responsibilities
* **Nakul Lagwal (AI & RAG Architecture Lead):** LLM integration (Ollama / Gemma 4:e2b), Prompt Engineering, Dual-Track RAG Orchestration, Intent Router, RapidFuzz Safety Valve, Conversational Memory.
* **Kavish Bansal (Backend & Database Engineer):** FastAPI architecture, PostgreSQL database schema, SQLAlchemy ORM models, ChromaDB client setup, Docker containerization, REST & streaming endpoints.
* **Vihaan Sharma (QA, Testing & Benchmarking Engineer):** Test query curation, precision/recall evaluation, latency & load profiling, hallucination detection, edge-case analysis, benchmarking reports.

---

## Week 1: Requirements, Architectural Blueprint & Foundation Setup
**Dates:** June 22, 2026 – June 28, 2026  
**Milestone:** Infrastructure initialization, base schema definition, and model environment configuration.

### Individual Contributions:
* **Nakul Lagwal (AI Lead):**
  * Evaluated local LLM execution capabilities on campus hardware; selected **Gemma 4 (e2b)** via Ollama for fast token generation and professional senior-level conversational tone.
  * Formulated initial system prompt rules to enforce zero-hallucination policies and strict adherence to university-provided documents.
  * Designed the theoretical **Dual-Track RAG** pipeline separating deterministic records from supplementary crawled data.

* **Kavish Bansal (Backend & Database):**
  * Configured `docker-compose.yml` orchestrating PostgreSQL (port 5433) and ChromaDB vector store (port 8001).
  * Initialized project directory architecture (`src/core`, `src/api`, `src/services`, `src/utils`, `scripts`).
  * Designed core relational schema for faculty profiles (`faculty` table) using SQLAlchemy declarative models in `src/services/db.py`.

* **Vihaan Sharma (QA & Testing):**
  * Compiled an initial benchmark set of 50 multi-category campus queries (academic schedules, faculty designations, fee structures, casual chitchat).
  * Created testing rubric and metrics tracking sheets for measuring retrieval accuracy, end-to-end response latency, and hallucination frequency.
  * Conducted initial sanity checks verifying Docker port bindings and service connectivity.

**Weekly Summary & Review:** Core tech stack verified. Docker orchestration running smoothly. Base schemas and LLM runtime established.

---

## Week 2: Core Backend Services, Intent Classification & Test Harness
**Dates:** June 29, 2026 – July 05, 2026  
**Milestone:** Functional FastAPI skeleton, early-exit chitchat router, and automated evaluation harnesses.

### Individual Contributions:
* **Nakul Lagwal (AI Lead):**
  * Developed `src/core/router.py` implementing an **Early-Exit Intent Router** to identify chitchat/out-of-scope queries prior to invoking heavy RAG components.
  * Configured keyword heuristics and canned responses to instantly terminate greeting flows in $<5\text{ ms}$.
  * Authored fact-mapping structures (`topics.json` and `juit_facts.json`) for instant extraction of official institutional facts.

* **Kavish Bansal (Backend & Database):**
  * Built the FastAPI application entry point (`src/main.py`) with asynchronous CORS middleware and health probe endpoints (`/health`).
  * Implemented database connection manager, session makers, and metadata loading hooks (`DatabaseService`).
  * Created database initialization scripts (`scripts/setup_db.py`) to automate PostgreSQL table creation.

* **Vihaan Sharma (QA & Testing):**
  * Created an automated Python test script to measure response times of the Early-Exit Intent Router vs full-pipeline queries.
  * Verified that common greetings ("hi", "hello", "who are you") bypassed database and LLM calls 100% of the time with near-zero latency.
  * Expanded the test query suite from 50 to 90 test cases, tagging queries by domain (admissions, faculty, hostel, chitchat).

**Weekly Summary & Review:** Intent routing operational. Zero compute wasted on chitchat. Base API routes active.

---

## Week 3: Dual-Track Retrieval, Data Seeding & Hybrid Indexing
**Dates:** July 06, 2026 – July 12, 2026  
**Milestone:** Relational database population, ChromaDB vector embedding integration, and Rank-BM25 hybrid search.

### Individual Contributions:
* **Nakul Lagwal (AI Lead):**
  * Implemented `HybridSearchService` (`src/services/hybrid_search.py`) integrating **Rank-BM25** lexical scoring with dense vector cosine similarity.
  * Designed context formatters to cleanly structure retrieved snippets with `--- TRACK A ---` and `--- TRACK B ---` trust headers for the LLM prompt.
  * Tuned embedding generation using `embeddinggemma:latest` for document chunks.

* **Kavish Bansal (Backend & Database):**
  * Authored data extraction and seeding scripts (`scripts/seed_faculty_from_mirror.py` and `scripts/seed_admin_staff.py`) using `BeautifulSoup4` to parse mirrored HTML into structured PostgreSQL records.
  * Implemented `VectorService` (`src/services/vector.py`) to interface with ChromaDB via HTTP client with distance-score thresholding.
  * Populated `luna_vault` collection with curated campus circulars and ordinances.

* **Vihaan Sharma (QA & Testing):**
  * Performed precision audits on retrieved faculty records, validating clean names, email addresses, and designations against official university directories.
  * Tested ChromaDB vector distance filtering under various distance thresholds to prevent out-of-domain chunks from leaking into Track B context.
  * Logged initial retrieval precision: Track A+ (Official Records) achieved 98.4%, while Track B hybrid search achieved 85.1%.

**Weekly Summary & Review:** Faculty profiles successfully ingested. Hybrid search functioning. Precision across Track A+ validated.

---

## Week 4: Streaming Generation, Safety Valves & Latency Profiling
**Dates:** July 13, 2026 – July 19, 2026  
**Milestone:** Real-time token streaming endpoints, RapidFuzz name ambiguity handler, and performance profiling.

### Individual Contributions:
* **Nakul Lagwal (AI Lead):**
  * Engineered the **Fuzzy Name Safety Valve** in `src/services/db.py` utilizing `rapidfuzz.process.extractOne` with `fuzz.WRatio`.
  * Set two-tier confidence thresholds: scores $\ge 80\%$ trigger direct profile retrieval; scores between $65\%$ and $79\%$ trigger interactive clarification prompts (*"Did you mean Dr. [Name]?"*).
  * Built conversational memory handling in `src/services/memory.py` using LangChain's `ChatMessageHistory` with session isolation.

* **Kavish Bansal (Backend & Database):**
  * Implemented asynchronous NDJSON streaming endpoint `POST /chat_stream` in `src/api/chat.py` using FastAPI's `StreamingResponse`.
  * Integrated multi-turn message history persistence and active session lifecycle management.
  * Added structured citation formatter (`src/utils/formatter.py`) appending source URLs and mandatory confidence disclaimers for Track B data.

* **Vihaan Sharma (QA & Testing):**
  * Designed an edge-case test suite specifically targeting faculty name typos, phonetic variations, and missing honorifics (e.g., "Prdeep Gupta", "Naveen Jglan").
  * Profiled time-to-first-token (TTFT) on `/chat_stream`, recording an average TTFT of $<350\text{ ms}$.
  * Verified that the "Did you mean...?" safety valve triggered consistently across 100% of ambiguous query permutations.

**Weekly Summary & Review:** Streaming chat functional. Typo handling and ambiguity detection working reliably. Latency profiled and optimized.

---

## Week 5: End-to-End Integration, Stress Testing & Hallucination Audits
**Dates:** July 20, 2026 – July 26, 2026  
**Milestone:** Full pipeline integration, system concurrency stress testing, and factual verification.

### Individual Contributions:
* **Nakul Lagwal (AI Lead):**
  * Conducted hallucination audits on Gemma 4:e2b responses; tightened system prompt constraints to force the model to output: *"I do not have that specific information in the official JUIT database"* when context is insufficient.
  * Refined Track B prompt templates to enforce transparent disclosure headers on supplementary document citations.
  * Connected web frontend injection script (`scripts/inject_widget.py`) with backend streaming endpoints.

* **Kavish Bansal (Backend & Database):**
  * Optimized PostgreSQL query indexes on `clean_name` and cached high-frequency lookup results in memory.
  * Hardened error handling in `/chat` and `/chat_stream` to gracefully catch database disconnections and vector store timeouts.
  * Unified service launch and process management within `run.sh` (automatic port clearance, Docker bootstrap, dual server startup).

* **Vihaan Sharma (QA & Testing):**
  * Executed concurrent load testing simulating simultaneous student sessions querying admission deadlines and fee structures.
  * Evaluated 150 benchmark queries across all three execution tracks (Chitchat, Track A+, Track B).
  * Compiled error logs and false-positive cases to guide final prompt adjustments and threshold calibrations.

**Weekly Summary & Review:** System stable under concurrent query loads. Strict prompt rules eliminated ungrounded LLM hallucinations.

---

## Week 6: Comprehensive Benchmarking, Documentation & Project Sign-Off
**Dates:** July 27, 2026 – August 02, 2026  
**Milestone:** Final metric validation, formal project documentation, and supervisor sign-off.

### Individual Contributions:
* **Nakul Lagwal (AI Lead):**
  * Drafted system architecture documentation and finalized Mermaid pipeline workflows.
  * Formalized the project report technical chapters (System Design, Dual-Track RAG Methodology, LLM Orchestration).
  * Packaged the codebase with clean modular separation and updated configuration environment profiles.

* **Kavish Bansal (Backend & Database):**
  * Finalized Docker container manifests, volume persistence scripts, and database backup routines.
  * Validated cold-start startup routines and automated dependency installations in `requirements.txt`.
  * Authored backend API reference documentation and deployment guides.

* **Vihaan Sharma (QA & Testing):**
  * Compiled the final **System Performance & Accuracy Report**:
    * **Chitchat Routing Precision:** 100% (Avg. Latency: 4.2 ms)
    * **Track A+ Official Record Precision:** 98.6% (Avg. Latency: 124 ms)
    * **Track B Supplementary Knowledge Precision:** 87.2% (Avg. Latency: 845 ms)
    * **Hallucination Rate:** 0% on official facts, <2.1% on supplementary web data
    * **Safety Valve Accuracy:** 100% on ambiguous name queries
  * Performed final regression testing on all endpoints prior to final project submission.

**Weekly Summary & Review:** 100% of project deliverables successfully completed, thoroughly tested, and documented.
