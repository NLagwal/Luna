# Luna - Intelligent Campus Assistant

Official enterprise conversational AI assistant for **Jaypee University of Information Technology (JUIT)**, Waknaghat, Solan, H.P. Built on a high-precision, bifurcated Dual-Track Retrieval-Augmented Generation (RAG) architecture.

---

## 🏛️ System Architecture

Luna decouples statutory university data from probabilistic web search using a **Bifurcated Dual-Track Retrieval** strategy:

* **Track A+ (Deterministic Ground Truth):**
  * **Fact Registry (`data/topics.json`, `data/juit_facts.json`):** Deterministic keyword-to-fact mapping with regex word-boundary matching and length-descending keyword priority.
  * **PostgreSQL Faculty & Staff Directory:** High-accuracy relational database with RapidFuzz `WRatio` matching, anchored name sanitization, and ambiguity safety gating.
* **Track B (Probabilistic Semantic Search):**
  * **ChromaDB Dense Vector Search:** Vector similarity retrieval ($dist \le 1.5$).
  * **Rank-BM25 Lexical Ranking:** Okapi BM25 keyword matching with local HTML mirror cold-start fallback.
  * **Trust Degradation Disclaimer:** Automatic confidence disclaimer on supplementary documents.
* **API Gateway & Client:**
  * Asynchronous FastAPI backend with NDJSON chunked streaming (`/chat_stream`) and conversational memory TTL pruning.
  * Zero-dependency embedded frontend widget (`luna-widget/luna-widget.js`) with DOM XSS escaping and per-user session isolation.

---

## 📁 Repository Directory Structure

```
Luna/
├── docker-compose.yml       # Microservices orchestration (PostgreSQL 17, ChromaDB)
├── run.sh                   # Main application launch script with health checks
├── requirements.txt         # Python package dependencies
├── README.md                # Project documentation and developer guide
├── .gitignore               # Git ignore rules
│
├── src/                     # Core backend application
│   ├── main.py              # FastAPI application entrypoint & startup lifecycle
│   ├── config.py            # Global configuration settings & environment vars
│   ├── api/                 # API routes (/chat, /chat_stream, /health)
│   ├── core/                # Business logic (Punctuation-agnostic IntentRouter)
│   ├── models/              # SQLAlchemy and Pydantic data models
│   └── services/            # Core services (Database, HybridSearch, LLM, Memory)
│
├── luna-widget/             # Embedded client chat widget
│   └── luna-widget.js       # Vanilla JS widget with DOM XSS sanitization
│
├── data/                    # Authoritative facts and registry mappings
│   ├── juit_facts.json      # Official university statutory facts
│   └── topics.json          # Keyword-to-fact topic index
│
├── reports/                 # Academic papers, technical specifications & PDFs
│   ├── Luna_Architecture_Document.pdf # 12-page compiled system architecture report
│   ├── Luna_Architecture_Document.tex # Complete LaTeX source
│   ├── Luna_Project_Diary.pdf         # 6-week engineering progress diary
│   ├── Luna_Project_Report.pdf        # Formal semester project report
│   └── PROJECT_DIARY.md               # Markdown engineering diary
│
├── benchmarks/              # Empirical evaluation suites & test logs
│   ├── results_50_questions.json      # 50/50 benchmark test results (100% pass)
│   └── benchmark_results.json         # Evaluation run metrics and latencies
│
├── scripts/                 # Utility scripts, data seeders, and evaluation tools
│   ├── generate_architecture_pdf.py   # Compiles architecture PDF to reports/
│   ├── test_50_questions.py           # Automated 50-question benchmark runner
│   ├── seed_faculty_from_mirror.py    # Scrapes & cleans faculty metadata
│   ├── seed_admin_staff.py            # Seeds administrative officers
│   └── setup_db.py                    # Initializes database tables
│
├── docs/                    # Architecture diagrams, specifications & design notes
│   ├── system_architecture.png        # High-level architecture topology diagram
│   └── documentation.md               # Additional architectural notes
│
├── logs/                    # Application and server logs (gitignored)
└── archive/                 # Historical diffs, scratch tools, and legacy tests
```

---

## 🚀 Quickstart Guide

### 1. Start Infrastructure
```bash
docker compose up -d
```

### 2. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Records
```bash
python -m scripts.setup_db
python -m scripts.seed_faculty_from_mirror
python -m scripts.seed_admin_staff
```

### 4. Launch Full Stack
```bash
./run.sh
```
* **Backend API:** `http://localhost:5000/health`
* **Mirrored Web Site with Widget:** `http://localhost:8000/www.juit.ac.in/index.html`

---

## 🧪 Running Benchmarks & Compiling Reports

* **Run 50-Question Benchmark Suite:**
  ```bash
  python -m scripts.test_50_questions
  ```
  Results will be saved in `benchmarks/results_50_questions.json`.

* **Recompile Architecture PDF:**
  ```bash
  python scripts/generate_architecture_pdf.py
  ```
  Compiled PDF will be output directly to `reports/Luna_Architecture_Document.pdf`.
