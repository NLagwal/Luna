# Luna - JUIT AI Assistant Documentation

## Application Overview
Luna is a modular RAG (Retrieval-Augmented Generation) application designed for Jaypee University of Information Technology (JUIT). It uses a hybrid retrieval strategy to provide deterministic answers for official records and high-precision semantic search for general website knowledge.

## Project Structure

```text
Luna/
├── src/                    # Core application logic
│   ├── main.py            # FastAPI entry point & app configuration
│   ├── api/
│   │   └── chat.py        # standard (/chat) and streaming (/chat_stream) endpoints
│   ├── core/
│   │   ├── config.py      # Environment variables and global settings
│   │   └── router.py      # Early-Exit Intent Router (Chitchat detection)
│   ├── services/
│   │   ├── db.py          # PostgreSQL/SQLAlchemy (Faculty & Fact Registry)
│   │   ├── llm.py         # LangChain & Ollama orchestration
│   │   ├── vector.py      # ChromaDB connection & similarity filtering
│   │   ├── hybrid_search.py # BM25 + Vector Search integration
│   │   └── memory.py      # Session-based conversational memory
│   └── utils/
│       └── formatter.py   # Response styling & deep citation formatting
├── scripts/                # Maintenance & Data Ingestion utilities
│   ├── setup_db.py        # Schema initialization for PostgreSQL
│   ├── seed_faculty.py    # Manual/Sample data seeding
│   ├── seed_faculty_from_mirror.py # Automated scraper for mirrored site
│   ├── ingest_html.py     # HTML to Vector DB (Track B) ingestion
│   └── ingest_vault.py    # Curated PDF ingestion utility
├── www.juit.ac.in/         # Local mirror of the university website
├── vault/                  # Curated directory for high-priority documents
├── docker-compose.yml      # Orchestration for PostgreSQL (5433) and ChromaDB (8001)
├── README.md               # Quick-start guide
└── requirements.txt        # Python dependencies
```

## Dual-Track Retrieval Logic

### Track A+ (Official Records)
- **Fact Registry:** Matches keywords against `topics.json` to pull official blocks from `juit_facts.json`.
- **Faculty Search:** Uses `rapidfuzz` against the PostgreSQL `faculty` table.
- **Safety Valve:** If a name match is between 65% and 79% confidence, Luna triggers a "Did you mean...?" response.
- **Trust Level:** Labeled as "Official Records" in the UI.

### Track B (Website Knowledge)
- **Hybrid Search:** Combines BM25 (keyword) and ChromaDB (vector) search.
- **Strict Filtering:** Only returns results if vector distance is within a high-relevance threshold.
- **Disclaimer:** Automatically prepends: *"Based on my search of university documents (which may be supplementary)..."*
- **Trust Level:** Labeled as "Website Knowledge".

## Technical Stack
- **Backend:** FastAPI, Uvicorn
- **Database:** PostgreSQL (Faculty), ChromaDB (Vectors)
- **LLM Engine:** Ollama (Gemma 4:e2b)
- **Orchestration:** LangChain
- **Search:** SQLAlchemy, RapidFuzz, Rank-BM25
- **Mirroring:** HTTrack (32-thread configuration)
