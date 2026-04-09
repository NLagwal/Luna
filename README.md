# LUNA: AI Assistant for JUIT Solan's Website

LUNA is an AI assistant for JUIT Solan's website, designed to provide quick and accurate information to users.

## Features

### Core Features (MVP)

*   **Citation Mapping:** Luna will provide citations for the information it provides, linking back to the source URL on the JUIT website.
*   **Vector-Based Search:** Instead of traditional keyword-based search, Luna will use a vector database (ChromaDB) to store and retrieve information from the entire website. This allows for more semantic and context-aware search.
*   **Local LLM Integration:** Luna will use local Large Language Models (LLMs) like `llama-3.1:8b` and `embeddinggemma` to process user queries and generate responses.

### Planned Features

*   **Website UI Integration:** The user interface for Luna will be designed to be cohesive with the existing JUIT website.
*   **PDF Querying:** Luna will be able to answer queries about the content of PDF files found on the website.

### Advanced RAG Optimizations

To enhance the system's performance, accuracy, and efficiency, especially with a large dataset, the following strategies will be considered:

*   **Multi-layered Retrieval:** Implement a tiered search system:
    1.  **Layer 1 (Curated Facts):** Utilize `juit_facts.json` for rapid, highly accurate answers to common, critical factual queries.
    2.  **Layer 2 (Prioritized RAG):** For other queries, search a prioritized subset of key documents (main web pages, recent PDFs).
    3.  **Layer 3 (Full RAG):** Expand to the entire archive of documents (including all PDFs) as a deep-search option.
*   **Query Understanding Enhancements:**
    *   **Query Rewriting/Expansion:** Use LLMs to refine or expand user queries for more effective searching.
    *   **Intent Classification:** Categorize user queries to route them to the most appropriate retrieval layer or data source.
    *   **HyDE (Hypothetical Document Embeddings):** Generate hypothetical answers to queries and embed them for a more semantically aligned search.
*   **Retrieval & Ranking Improvements:**
    *   **Hybrid Search:** Combine vector similarity search with keyword-based search (e.g., BM25) with vector search for comprehensive results.
    *   **Re-ranking:** Apply secondary models to re-rank initial retrieval results, selecting the most relevant chunks for the LLM.
    *   **Metadata Filtering:** Leverage document metadata (e.g., year, department, document type) to pre-filter search results, dramatically increasing relevance and speed.
*   **LLM Generation Optimizations:**
    *   **Caching:** Store and reuse generated responses for frequently asked questions.
    *   **Streaming Responses:** Deliver LLM output token-by-token for a more responsive user experience.

### Example Usage

**User:** Who is Nishant Jain?
**Luna:** Nishant Jain is a faculty member with XYZ qualifications. [Learn more](link-to-source)

**User:** Tell me about the XYZ event.
**Luna:** The XYZ event is scheduled for [timestamp]. [View event details](link-to-event-page-or-pdf]
