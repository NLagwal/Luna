# LUNA: Technical Deep Dive & Architectural Specifications

LUNA is a high-precision, Retrieval-Augmented Generation (RAG) ecosystem specifically engineered for the **Jaypee University of Information Technology (JUIT)**. It transcends standard RAG implementations by employing a **Dual-Track Retrieval Architecture** designed to eliminate hallucinations in high-stakes university data.

---

## 1. System Architecture Overview

LUNA is built on a modular, local-first stack to ensure data privacy and low-latency performance.

### Core Tech Stack
| Component | Technology | Role |
| :--- | :--- | :--- |
| **Orchestrator** | FastAPI (Python 3.13) | Backend API & Logic |
| **LLM Engine** | Ollama (`dolphin-llama3:latest`) | Text generation and reasoning |
| **Embeddings** | Ollama (`embeddinggemma:latest`) | Semantic vector generation (1024-dim) |
| **Vector DB** | ChromaDB (Dockerized, Port 8001) | High-speed semantic search |
| **Frontend** | Vanilla JavaScript / CSS | Embeddable chat widget |
| **Fuzzy Matching** | `rapidfuzz` | Entity recognition and typo tolerance |

---

## 2. The Dual-Track Retrieval Engine

The "brain" of LUNA is its `Selective Retrieval Strategy`, implemented in `app.py`. It categorizes incoming queries into two distinct pipelines:

### Track A: Deterministic Knowledge (Short-Circuit)
When LUNA identifies a query about a specific entity (e.g., a Professor) or a "Hard Fact" (e.g., Fees), it triggers a short-circuit mechanism:
- **Entity Recognition**: Uses `rapidfuzz` (WRatio scorer, threshold 80) to match names against a pre-built `faculty_structured_db.json`.
- **Hard Facts**: Scans for keywords related to fees, leadership (VC, Registrar), or university establishment in `juit_facts.json`.
- **Hallucination Protection**: If a match is found, **Vector DB retrieval is bypassed**. This prevents "data leakage" where chunks from different professors might be mixed into a single response, ensuring 100% factual accuracy for people.

### Track B: Semantic RAG (Deep Context)
For general queries (e.g., "What is the policy on X?" or "Tell me about the CSE department"), LUNA falls back to semantic search:
- **Search Logic**: Queries ChromaDB for the Top-5 most relevant chunks.
- **Context Synthesis**: Combines any discovered structured facts with the vector search results to provide a comprehensive answer.

---

## 3. Data Processing Pipeline

LUNA's reliability comes from its multi-stage data refinement process.

### Phase 1: Intelligent Parsing (`parser.py`)
Raw HTML/PHP files scraped from the JUIT website are transformed into clean, searchable text:
- **Targeted Extraction**: Specifically targets `div#container` and `div.department-right` to ignore navigation sidebars and footers.
- **Noise Filtering**: Automatically discards 404 pages, login forms, and system utilities.
- **Tag Stripping**: Removes scripts, styles, and noscript tags while preserving whitespace for readability.

### Phase 2: Structural Extraction (`build_faculty_db.py`)
Specifically targets faculty profiles (`faculty.php?id=*`):
- **Section Parsing**: Isolates Biography, Research Interests, and Open Projects into structured JSON fields.
- **Deduplication**: Resolves multiple versions of the same faculty page by selecting the one with the highest information density.

### Phase 3: Vector Ingestion (`ingest.py`)
Populates the semantic memory of the system:
- **Chunking Strategy**: Uses `RecursiveCharacterTextSplitter` with a `chunk_size` of 1500 and `overlap` of 300 characters.
- **PDF Integration**: Extracts text from high-utility documents (Syllabi, Fees, Calendars) using `PyMuPDF`.
- **URL Mapping**: Each chunk is tagged with its original `https://www.juit.ac.in/` source URL for deterministic citations.

---

## 4. Frontend Integration & UX

The user interacts with LUNA via a lightweight, zero-dependency widget located in `/luna-widget/`.

- **Streaming Implementation**: Uses `fetch` with the `ReadableStream` API to process tokens in real-time from the `/chat_stream` endpoint.
- **Citation System**: Automatically appends reference links to the end of messages, allowing users to verify the source of the AI's information.
- **Visual Integration**: Styles are encapsulated in `luna-style.css`, designed to float over the existing university website seamlessly.
- **Automation**: `inject_widget.py` provides a script to recursively inject the widget into thousands of scraped HTML files, facilitating a full-site demo.

---

## 5. Security & Verification

LUNA enforces strict constraints on the LLM via its system prompt:
1. **Source Lockdown**: The LLM is forbidden from using external training data for university-specific facts.
2. **Negative Constraint**: If no data is found in the provided records, it must explicitly state its lack of information rather than guessing.
3. **Factual Integrity**: Summaries of faculty profiles must be verbatim or high-fidelity to the source JSON.

---

## 6. Current Database Statistics
- **Structured Faculty**: 100+ cleaned profiles.
- **Vector Chunks**: ~28,000+ segments from HTML and PDF sources.
- **Embedding Dimensions**: 1024 (Google Gemma model).
