# SPEC.md: Luna AI Assistant for JUIT Solan

## 1. Project Overview
Luna is a RAG-based (Retrieval-Augmented Generation) AI assistant for the JUIT Solan website. It uses local LLMs and vector databases to provide accurate, cited answers directly through a chat interface integrated into the scraped site.

## 2. Technical Stack
- **Orchestrator:** LangChain (Python)
- **Large Language Model:** `llama-3.1:8b` (via Ollama)
- **Embedding Model:** `embeddinggemma:latest` (via Ollama)
- **Vector Database:** ChromaDB (Running in Docker)
- **Backend API:** FastAPI (Handling chat requests)
- **PDF Extraction:** PyMuPDF (For selected high-value PDFs)
- **Frontend Integration:** Vanilla JS Chat Widget injected into JUIT HTML files.

## 3. Data Ingestion Pipeline (`ingest.py`)
### 3.1 HTML & PDF Processing
- **HTML:** Source is `/PARSED_SHIT/`. Metadata includes `source_url` mapped from local paths to `https://www.juit.ac.in/`.
- **PDFs:** Selective parsing of ~50 high-utility PDFs (Calendars, Syllabi, Notices).
- **Chunking:** `RecursiveCharacterTextSplitter` from LangChain.
  - Chunk Size: 1000 characters.
  - Chunk Overlap: 100 characters.

### 3.2 Vector Storage
- **ChromaDB:** Running as a persistent service in Docker (Port 8000).
- **Embeddings:** `embeddinggemma:latest` used to generate 1024-dimensional vectors.
- **Persistence:** Data stored in `./chroma_data`.

## 4. Backend System (`app.py`)
- **Framework:** FastAPI.
- **Endpoints:**
  - `POST /chat`: Receives `{ "message": "..." }`, performs RAG, returns `{ "response": "...", "citations": [...] }`.
- **RAG Chain:**
  1. Receive query.
  2. Embed query using `embeddinggemma:latest`.
  3. Retrieve top-k chunks from ChromaDB.
  4. Prompt `llama-3.1:8b` with context + query.
  5. Format response with citations.

## 5. UI Integration (`luna-widget/`)
- **`luna-widget.js`**: Handles the chat UI, message history, and API calls to the FastAPI backend.
- **`luna-style.css`**: Styles the floating chat bubble and window (Cohesive with JUIT theme).
- **Injection Script (`inject_widget.py`)**: 
  - Recursively crawls `www.juit.ac.in` and `PARSED_SHIT`.
  - Injects `<link rel="stylesheet" href="/luna-widget/luna-style.css">` and `<script src="/luna-widget/luna-widget.js"></script>` before the `</body>` tag.

## 6. Docker Configuration (`docker-compose.yml`)
- Container: `chromadb/chroma:latest`.
- Port Mapping: `8000:8000`.
- Environment: `IS_PERSISTENT=TRUE`, `ANONYMIZED_TELEMETRY=FALSE`.
