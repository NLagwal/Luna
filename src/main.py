from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.chat import router as chat_router
from src.services.hybrid_search import hybrid_search_service
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize BM25 search index from Chroma collection
    hybrid_search_service.initialize_from_chroma()
    yield

app = FastAPI(title="Luna - JUIT AI Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, tags=["chat"])

import os
from fastapi.staticfiles import StaticFiles

if os.path.exists("luna-widget"):
    app.mount("/luna-widget", StaticFiles(directory="luna-widget"), name="luna-widget")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
