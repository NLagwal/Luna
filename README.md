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

### Example Usage

**User:** Who is Nishant Jain?
**Luna:** Nishant Jain is a faculty member with XYZ qualifications. [Learn more](link-to-source)

**User:** Tell me about the XYZ event.
**Luna:** The XYZ event is scheduled for [timestamp]. [View event details](link-to-event-page-or-pdf)
