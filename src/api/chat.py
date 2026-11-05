from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from src.core.config import settings
from src.core.router import IntentRouter
from src.services.db import db_service
from src.services.llm import llm_service
from src.services.memory import memory_service
from src.services.hybrid_search import hybrid_search_service
from src.utils.formatter import ResponseFormatter

router = APIRouter()

def get_rag_context(query: str, session_id: str = "default"):
    import re
    query_lower = query.lower().strip()
    
    # 0. Clean Query for Person Search
    # Strip common inquiry phrases and possessives
    noise = [
        "who is", "tell me about", "dr.", "prof.", "professor", "faculty", 
        "biography", "research interests", "research papers", "contact", 
        "details", "information", "'s", "projects", "office"
    ]
    clean_query = query_lower
    for word in noise:
        clean_query = clean_query.replace(word, "")
    clean_query = " ".join(clean_query.split()).strip()
    
    structured_context = []
    urls = []
    trust_level = "A" # Default to Track A
    is_person = False
    ambiguity_suggestion = None

    # 1. Track A+: Fact Registry
    fact = db_service.get_fact(query)
    if fact:
        text = fact.get("text", "")
        structured_context.append(f"UNIVERSITY FACT: {text}")
        if fact.get("ref"): urls.append(fact["ref"])
        if session_id:
            for name, fac_id in db_service.name_to_id.items():
                if len(name) > 5 and name in text.lower():
                    memory_service.set_session_context(session_id, "active_faculty_id", fac_id)
                    memory_service.set_session_context(session_id, "active_faculty_name", name)
                    break

    # 2. Track A+: Faculty Search with Safety Valve
    teacher_markers = ["dr.", "prof.", "professor", "faculty", "who is", "biography", "research interests"]
    has_teacher_marker = any(marker in query_lower for marker in teacher_markers)

    if has_teacher_marker:
        match = db_service.fuzzy_search_faculty(clean_query)
        if match:
            name, score, index = match
            if score >= settings.FUZZY_MATCH_THRESHOLD:
                is_person = True
                faculty_id = db_service.name_to_id.get(name)
                profile = db_service.get_faculty_by_id(faculty_id)
                if profile:
                    structured_context.append(ResponseFormatter.format_faculty_profile(profile))
                    if profile.source_url: urls.append(profile.source_url)
                    if profile.profile_pdf: urls.append(profile.profile_pdf)
                    if session_id:
                        memory_service.set_session_context(session_id, "active_faculty_id", profile.id)
                        memory_service.set_session_context(session_id, "active_faculty_name", profile.name)
            elif score >= settings.AMBIGUITY_THRESHOLD and not structured_context:
                ambiguity_suggestion = name
    elif len(clean_query) > 3:
        # If no explicit teacher marker, only match high-confidence full names
        match = db_service.fuzzy_search_faculty(clean_query)
        if match:
            name, score, index = match
            if score >= settings.FUZZY_MATCH_THRESHOLD:
                is_person = True
                faculty_id = db_service.name_to_id.get(name)
                profile = db_service.get_faculty_by_id(faculty_id)
                if profile:
                    structured_context.append(ResponseFormatter.format_faculty_profile(profile))
                    if profile.source_url: urls.append(profile.source_url)
                    if profile.profile_pdf: urls.append(profile.profile_pdf)
                    if session_id:
                        memory_service.set_session_context(session_id, "active_faculty_id", profile.id)
                        memory_service.set_session_context(session_id, "active_faculty_name", profile.name)

    # 2b. Conversational Coreference / Follow-up Resolution
    if not is_person and session_id:
        session_ctx = memory_service.get_session_context(session_id)
        active_faculty_id = session_ctx.get("active_faculty_id")
        if active_faculty_id:
            pronoun_pattern = r'\b(he|him|his|she|her|hers|they|them|their|this professor|this teacher|this faculty|the professor|the teacher|the faculty)\b'
            has_pronoun = bool(re.search(pronoun_pattern, query_lower))
            followup_words = [
                "grants", "grant", "projects", "project", "research", "publications", 
                "papers", "books", "patents", "teaching", "qualifications", 
                "experience", "contact", "email", "office", "phd", "students", 
                "awards", "salary", "in depth", "more about", "tell me more"
            ]
            has_followup_word = any(w in query_lower for w in followup_words)
            
            if has_pronoun or (len(query.split()) <= 6 and has_followup_word):
                profile = db_service.get_faculty_by_id(active_faculty_id)
                if profile:
                    is_person = True
                    structured_context.append(ResponseFormatter.format_faculty_profile(profile))
                    if profile.source_url: urls.append(profile.source_url)
                    if profile.profile_pdf: urls.append(profile.profile_pdf)
                    
                    # Search documents enriched with faculty name
                    enriched_query = f"{profile.name} {clean_query}"
                    docs = hybrid_search_service.search(enriched_query)
                    if docs:
                        vector_text = "\n\n".join([doc.page_content for doc in docs[:3]])
                        structured_context.append(f"SUPPLEMENTARY FACULTY DOCUMENTS: {vector_text}")
                        urls.extend([doc.metadata.get("source_url") for doc in docs if doc.metadata.get("source_url")])

    # 3. Track B: Hybrid Search (if not a specific person match or if more info needed)
    if not is_person and not ambiguity_suggestion:
        docs = hybrid_search_service.search(query)
        if docs:
            # Only demote to Track B if no high-trust Fact or Profile was found
            if not structured_context:
                trust_level = "B"
            
            vector_text = "\n\n".join([doc.page_content for doc in docs])
            structured_context.append(f"WEBSITE DATA: {vector_text}")
            urls.extend([doc.metadata.get("source_url") for doc in docs if doc.metadata.get("source_url")])

    # Clean urls of None or empty strings and deduplicate preserving order
    seen = set()
    clean_urls = []
    for u in urls:
        if u and isinstance(u, str) and u.strip():
            u_clean = u.strip()
            if u_clean not in seen:
                seen.add(u_clean)
                clean_urls.append(u_clean)
    return "\n\n".join(structured_context), clean_urls, trust_level, ambiguity_suggestion

@router.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_query = body.get("message")
    session_id = body.get("session_id", "default")
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Message is required")

    # 1. Early-Exit Intent Routing
    intent = IntentRouter.classify(user_query)
    if intent == "chitchat":
        return {"response": IntentRouter.get_chitchat_response(user_query), "citations": [], "trust_level": "A"}

    # 2. RAG Context Retrieval
    context, urls, trust_level, ambiguity = get_rag_context(user_query, session_id)
    
    if ambiguity:
        return {
            "response": f"I couldn't find a perfect match for '{user_query}'. Did you mean {ambiguity}? If so, please ask specifically about them.",
            "citations": [],
            "trust_level": "A"
        }

    # 3. LLM Generation
    history = memory_service.get_session_history(session_id)
    chain = llm_service.get_chain()
    
    # Pre-formatting for prompt
    formatted_context = f"--- TRACK {trust_level} RECORDS ---\n{context}"
    print(f"DEBUG: Formatted Context: {formatted_context}")
    
    try:
        response = chain.invoke({
            "context": formatted_context,
            "question": user_query,
            "history": history.messages
        })
        
        # 4. Memory Update
        history.add_user_message(user_query)
        history.add_ai_message(response)
        
        # 5. Formatting
        full_response = response + ResponseFormatter.format_source_footer(urls, trust_level)
        return {"response": full_response, "citations": urls, "trust_level": trust_level}
    except Exception as e:
        return {
            "response": f"I encountered an error processing your request: {str(e)}",
            "citations": [],
            "trust_level": "A"
        }

@router.post("/chat_stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_query = body.get("message")
    session_id = body.get("session_id", "default")
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Message is required")

    intent = IntentRouter.classify(user_query)
    if intent == "chitchat":
        async def stream_chitchat():
            yield json.dumps({"token": IntentRouter.get_chitchat_response(user_query)}) + "\n"
        return StreamingResponse(stream_chitchat(), media_type="application/x-ndjson")

    context, urls, trust_level, ambiguity = get_rag_context(user_query, session_id)

    if ambiguity:
        async def stream_ambiguity():
            yield json.dumps({"token": f"I couldn't find a perfect match for '{user_query}'. Did you mean {ambiguity}? If so, please ask specifically about them."}) + "\n"
        return StreamingResponse(stream_ambiguity(), media_type="application/x-ndjson")

    async def generate_rag():
        try:
            history = memory_service.get_session_history(session_id)
            chain = llm_service.get_chain()
            formatted_context = f"--- TRACK {trust_level} RECORDS ---\n{context}"
            
            full_response = ""
            async for chunk in chain.astream({
                "context": formatted_context,
                "question": user_query,
                "history": history.messages
            }):
                if chunk:
                    full_response += chunk
                    yield json.dumps({"token": chunk}) + "\n"
                    await asyncio.sleep(0.01)
            
            history.add_user_message(user_query)
            history.add_ai_message(full_response)
            
            yield json.dumps({"citations": urls or [], "trust_level": trust_level}) + "\n"
        except Exception as e:
            yield json.dumps({"error": f"An error occurred while generating response: {str(e)}"}) + "\n"

    return StreamingResponse(generate_rag(), media_type="application/x-ndjson")

