import chromadb
from langchain_chroma import Chroma
from src.core.config import settings
from src.services.llm import llm_service

class VectorService:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST, 
            port=settings.CHROMA_PORT
        )
        self.vector_store = Chroma(
            client=self.client,
            collection_name=settings.COLLECTION_NAME,
            embedding_function=llm_service.embeddings,
        )

    def similarity_search_with_threshold(self, query: str, k: int = 4):
        # Using similarity_search_with_relevance_scores or custom logic
        # Chroma distance is often L2 or Cosine. We'll use a manual filter.
        try:
            if not self.vector_store._embedding_function:
                return []
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
            print(f"DEBUG: Vector search for '{query}' scores: {[s for d, s in docs_and_scores]}")
            
            # Filter based on threshold (assuming distance where lower is better)
            filtered_docs = []
            for doc, score in docs_and_scores:
                if score <= settings.VECTOR_DISTANCE_THRESHOLD:
                    filtered_docs.append(doc)
            return filtered_docs
        except Exception as e:
            print(f"DEBUG: Vector search unavailable ({e}); falling back.")
            return []


vector_service = VectorService()
