from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from rapidfuzz import process, utils
import uvicorn
import os
import chromadb
import json
import asyncio
import glob
import string

from sqlalchemy import create_engine, text as sql_text
from sqlalchemy.orm import sessionmaker

# Config
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
EMBED_MODEL = "embeddinggemma:latest"
LLM_MODEL = "gemma4:e2b"
COLLECTION_NAME = "juit_knowledge_base"
ROOT_DIR = "/home/lag/Projekt/Luna/"
PARSED_DIR = os.path.join(ROOT_DIR, "PARSED_SHIT")
DB_URL = "postgresql://postgres:root@localhost:5432/padhai_app_db"

# Load Facts (Structured)
try:
    with open("juit_facts.json", "r") as f:
        FACTS_DB = json.load(f)
except Exception:
    FACTS_DB = {}

# Load Faculty Database (Structured) - Try Database first, then fallback to JSON
FACULTY_DB = {}
try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(sql_text("SELECT * FROM faculty"))
        columns = result.keys()
        for row in result:
            profile = dict(zip(columns, row))
            FACULTY_DB[profile['id']] = profile
    print(f"LOADED {len(FACULTY_DB)} profiles from Postgres Database.", flush=True)
except Exception as e:
    print(f"DATABASE LOAD FAILED: {e}. Falling back to JSON...", flush=True)
    try:
        with open("faculty_structured_db.json", "r") as f:
            FACULTY_DB = json.load(f)
    except Exception:
        FACULTY_DB = {}

# Pre-calculate search keys for fuzzy matching
FACULTY_NAMES = [p['clean_name'] for p in FACULTY_DB.values()]
NAME_TO_FID = {p['clean_name']: fid for fid, p in FACULTY_DB.items()}


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Pipeline
embeddings = OllamaEmbeddings(model=EMBED_MODEL)
llm = OllamaLLM(model=LLM_MODEL, timeout=120)

# Connect to ChromaDB
vector_store = Chroma(
    client=chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT),
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

# Template for RAG
prompt_template = """You are Luna, the official senior AI assistant for Jaypee University of Information Technology (JUIT) Solan. 

STRICT RULE: Use ONLY the 'PROVIDED RECORDS' below. 
Do not use any external knowledge about people or the university. 
If the information is not in the records, say "I do not have that specific information in the official JUIT database."

If you are provided with a 'FACULTY PROFILE', summarize it exactly as written. 
Do not add startups, publications, or degrees that are not explicitly in that profile text.

PROVIDED RECORDS:
{context}

User Question:
{question}

Official Answer: """
PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

def get_structured_context(query: str):
    query_lower = query.lower().strip()
    # Clean query for name matching
    clean_query = query_lower.replace("who is", "").replace("tell me about", "").replace("dr.", "").replace("prof.", "").replace("dr", "").replace("prof", "").strip()
    clean_query = clean_query.translate(str.maketrans('', '', string.punctuation)).strip()
    
    structured_context = []
    urls = []
    is_person_query = False

    # 1. Check Hard Facts (Fees, etc)
    fact_topics = {
        "fee": "fee structure", "tuition": "fee structure", "hostel": "fee structure",
        "faculty strength": "faculty count", "faculty count": "faculty count",
        "vice chancellor": "vice chancellor", "vc": "vice chancellor",
        "registrar": "registrar", "established": "establishment", "location": "location"
    }
    for keyword, key in fact_topics.items():
        if keyword in query_lower:
            fact = FACTS_DB.get(key)
            if fact:
                if isinstance(fact, dict):
                    # Use verbose fact if requested or by default, include ref
                    text = fact.get("verbose", fact.get("text", ""))
                    ref = fact.get("ref", "")
                    structured_context.append(f"UNIVERSITY FACT: {text}")
                    if ref: urls.append(ref)
                else:
                    structured_context.append(f"UNIVERSITY FACT: {fact}")
                    urls.append("juit_facts.json")
            break

    # 2. Fuzzy Faculty Search
    if len(clean_query) > 3:
        # Correct rapidfuzz usage
        from rapidfuzz import fuzz
        match = process.extractOne(clean_query, FACULTY_NAMES, scorer=fuzz.WRatio, processor=utils.default_process)
        print(f"DEBUG: Fuzzy match for '{clean_query}': {match}", flush=True)
        
        if match and match[1] >= 80: # Using WRatio, 80 is a good confidence threshold
            matched_name = match[0]
            fid = NAME_TO_FID[matched_name]
            profile = FACULTY_DB[fid]
            print(f"DEBUG: Selected Profile: {profile['name']} (ID: {fid})", flush=True)
            
            p_data = f"FACULTY PROFILE: {profile['name']}\n"
            p_data += f"Designation: {profile['designation']}\n"
            if profile.get('contact_info'): p_data += f"Contact: {profile['contact_info']}\n"
            if profile.get('profile_pdf'): p_data += f"Detailed Profile (PDF): {profile['profile_pdf']}\n"
            if profile['biography']: p_data += f"Biography: {profile['biography']}\n"
            if profile['research_interests']: p_data += f"Research Interests: {profile['research_interests']}\n"
            if profile['open_projects']: p_data += f"Projects: {profile['open_projects']}\n"
            
            # Additional Info
            if profile.get('additional_info'):
                for key, val in profile['additional_info'].items():
                    p_data += f"{key}: {val}\n"
            
            # Publications
            if profile.get('publication_profiles'):
                p_data += "Publication Profiles: " + ", ".join([f"{k}: {v}" for k, v in profile['publication_profiles'].items()]) + "\n"
            if profile.get('publication_counts'):
                p_data += "Publication Summary: " + ", ".join([f"{yr} ({count})" for yr, count in profile['publication_counts'].items()]) + "\n"
            
            structured_context.append(p_data)
            urls.append(profile['source_url'])
            if profile.get('profile_pdf'): urls.append(profile['profile_pdf'])
            is_person_query = True

    return "\n\n".join(structured_context), urls, is_person_query

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_query = body.get("message")
    if not user_query: return {"error": "Message is required"}

    # 1. Get structured data
    structured_text, structured_urls, is_person = get_structured_context(user_query)
    
    # 2. Hybrid Logic: If we found a specific person, SHORT-CIRCUIT and skip Vector DB
    # This prevents the AI from mixing in info from other professors.
    if is_person:
        final_context = f"--- OFFICIAL JUIT FACULTY RECORD ---\n{structured_text}"
        all_urls = structured_urls
    else:
        # Use Vector DB for general questions
        clean_query = user_query.replace("?", "").replace("!", "").strip()
        docs = vector_store.similarity_search(clean_query, k=5)
        vector_text = "\n\n".join([doc.page_content for doc in docs])
        vector_urls = [doc.metadata.get("source_url") for doc in docs if doc.metadata.get("source_url")]
        
        final_context = f"--- STRUCTURED DATA ---\n{structured_text}\n\n--- ADDITIONAL WEBSITE DATA ---\n{vector_text}"
        all_urls = list(set(structured_urls + vector_urls))
    
    # 3. Generate
    full_prompt = PROMPT.format(context=final_context, question=user_query)
    answer = llm.invoke(full_prompt)
    
    if all_urls:
        answer += "\n\nSources:\n" + "\n".join([f"- {url}" for url in all_urls])

    return {"response": answer, "citations": all_urls}

@app.post("/chat_stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_query = body.get("message")
    if not user_query: return {"error": "Message is required"}

    structured_text, structured_urls, is_person = get_structured_context(user_query)

    async def generate_rag():
        try:
            if is_person:
                final_context = f"--- OFFICIAL JUIT FACULTY RECORD ---\n{structured_text}"
                all_urls = structured_urls
            else:
                clean_query = user_query.replace("?", "").replace("!", "").strip()
                docs = vector_store.similarity_search(clean_query, k=5)
                vector_text = "\n\n".join([doc.page_content for doc in docs])
                vector_urls = [doc.metadata.get("source_url") for doc in docs if doc.metadata.get("source_url")]
                final_context = f"--- STRUCTURED DATA ---\n{structured_text}\n\n--- ADDITIONAL WEBSITE DATA ---\n{vector_text}"
                all_urls = list(set(structured_urls + vector_urls))
            
            full_prompt = PROMPT.format(context=final_context, question=user_query)
            
            for chunk in llm.stream(full_prompt):
                yield json.dumps({"token": chunk}) + "\n"
                await asyncio.sleep(0.01)
            
            if all_urls:
                yield json.dumps({"citations": all_urls}) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(generate_rag(), media_type="application/x-ndjson")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
