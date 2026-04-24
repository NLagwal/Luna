# LUNA: Precision AI Assistant for JUIT Solan

LUNA is a high-accuracy, RAG-powered AI assistant specifically engineered for the Jaypee University of Information Technology (JUIT) website. Unlike standard RAG systems, LUNA uses a dual-track retrieval architecture to eliminate hallucinations and ensure deterministic correctness for university data.

## 🚀 Actual Architecture

LUNA operates on a **Selective Retrieval Strategy** that chooses the best data source based on query intent:

### 1. Deterministic Knowledge Track (100% Accuracy)
*   **Structured Faculty DB (`faculty_structured_db.json`)**: Contains cleaned, parsed profiles for 100+ faculty members (Biography, Research, Projects).
*   **Hard Facts DB (`juit_facts.json`)**: Stores "Ground Truth" data for fees (2026-27), university leadership (VC, Registrar), and establishment details.
*   **Hallucination Protection**: When a person or hard fact is identified, LUNA **short-circuits** the Vector DB. This prevents "data leakage" where details from one professor might accidentally mix into another's biography.

### 2. Semantic RAG Track (Deep Context)
*   **Vector Database**: ChromaDB (running in Docker) storing 28,000+ text chunks from the entire JUIT website and high-utility PDFs.
*   **Content Filtering**: Custom parser (`parser.py`) that strips navigation noise and filters out 404 pages, login forms, and junk content.
*   **Semantic Search**: Uses `embeddinggemma:latest` to find relevant information for general queries (e.g., "What is the policy on X?").

## 🛠 Technical Stack

*   **LLM**: `llama3:latest` (via Ollama)
*   **Embeddings**: `embeddinggemma:latest` (via Ollama)
*   **Vector Store**: ChromaDB
*   **API**: FastAPI (Python 3.13)
*   **Entity Matching**: `rapidfuzz` (Fuzzy name matching for typos like "Kushal Kunwar" -> "Kushal Kanwar")

## 📂 Key Components

*   `app.py`: Core API server with selective retrieval logic and hallucination short-circuits.
*   `build_faculty_db.py`: Structured scraper that extracts core biographical data from faculty pages.
*   `parser.py`: Advanced HTML/PHP parser that targets main content areas (`div#container`) and cleans data.
*   `ingest.py`: Chunking and vectorization pipeline for the ChromaDB knowledge base.
*   `juit_facts.json`: The "Hard Fact" repository for fees and leadership.

## 🚦 How It Runs

1.  **Parsing**: Run `python3 parser.py` to extract clean text from the scraped site.
2.  **Structuring**: Run `python3 build_faculty_db.py` to create the deterministic entity database.
3.  **Ingestion**: Run `.venv/bin/python3 ingest.py` to populate the vector store.
4.  **Serving**: Run `.venv/bin/python3 app.py` to start the assistant on port 5000.

## ✅ Verification Example

*   **Query**: "Who is Dr. Kushal Kunwar?"
*   **Logic**: 
    1. Fuzzy match identifies "Kushal Kanwar" (Score > 80).
    2. Short-circuit: Vector DB is disabled.
    3. Retrieval: Pulls exact PhD and Project data from `faculty_structured_db.json`.
    4. Result: 100% accurate profile without cross-contamination from other faculty.
