# MVP SHIT (Eve)
## GOTTA MAP THE CITATION TO URL.
// Ex: IF the model quotes something in url xyz.com/abc,
// the CITATION is given in the model's answer.
## EMBEDDING MODEL SHIT & CHROMADB SHIT
// Ex: Instead of actual queries, we gon use vectordb
// to chunk and store the whole site.
## LLM CONNECTION SHIT
TO USE: ANY LOCAL LLM will work with TOOL to query the 
vectordb + to calculate embedding val for a QUERY.
Models: llama-3.1:8b and embeddinggemma

# EXTRA SHIT (nacht)
## ACTUAL SITE UI SHIT 
MUST LOOK COHESIVE ON JUIT's WEBSITE.

## ACTUAL DEMO SHIT
MUST be able to query SOME pdf files. SOME*****

> Example flow: 
user: Who the fuck is nishant jain?
Luna: Nishant jain is xyz faculty with abc qualifications
wanna know more? (citation to the site)

> Example flow:
user: Tell me info about xyz event!
Luna: xyz fuckass event is happening in WHATEVER timestamp
(citation to the event LINK or PDF.)

# OPTIMIZATION SHIT
## LAYERED RETRIEVAL STRATEGY
// Use juit_facts.json first for critical facts, then prioritized RAG, then full archive.
## QUERY OPTIMIZATIONS
// Query Rewriting/Expansion, Intent Classification, HyDE for better search.
## RETRIEVAL & RANKING OPTIMIZATIONS
// Hybrid Search (keyword + vector), Re-ranking retrieved chunks, Parent Document Retrieval.
## DATA PROCESSING OPTIMIZATIONS
// Metadata Filtering for efficient search, Smart Chunking.
## LLM GENERATION OPTIMIZATIONS
// Caching common answers, Streaming responses.

