from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from src.services.vector import vector_service

class HybridSearchService:
    def __init__(self):
        self.bm25 = None
        self.documents = []
    
    def initialize_bm25(self, docs):
        self.documents = docs
        tokenized_corpus = [doc.page_content.lower().split() for doc in docs]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def initialize_from_chroma(self):
        try:
            col = vector_service.vector_store._collection
            count = col.count()
            if count > 0:
                res = col.get(include=["documents", "metadatas"])
                docs = []
                for doc_text, meta in zip(res.get("documents", []), res.get("metadatas", [])):
                    if doc_text:
                        docs.append(Document(page_content=doc_text, metadata=meta or {}))
                if docs:
                    self.initialize_bm25(docs)
                    print(f"BM25 initialized successfully with {len(docs)} documents from Chroma.")
                    return
        except Exception as e:
            print(f"Failed to initialize BM25 from Chroma: {e}")

        # Fallback: Index local mirror documents so BM25 is never empty
        try:
            import os
            from bs4 import BeautifulSoup
            from src.core.config import settings
            mirror_dir = os.path.join(settings.ROOT_DIR, "www.juit.ac.in")
            docs = []
            if os.path.exists(mirror_dir):
                for root, _, files in os.walk(mirror_dir):
                    for file in files:
                        if file.endswith((".html", ".htm")):
                            path = os.path.join(root, file)
                            try:
                                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                                    soup = BeautifulSoup(fp.read()[:6000], "html.parser")
                                    for s in soup(["script", "style"]):
                                        s.decompose()
                                    t = " ".join(soup.get_text().split())
                                    if len(t) > 100:
                                        rel_path = os.path.relpath(path, mirror_dir)
                                        docs.append(Document(
                                            page_content=t[:1200],
                                            metadata={"source_url": f"https://www.juit.ac.in/{rel_path}"}
                                        ))
                            except Exception:
                                continue
            if docs:
                self.initialize_bm25(docs)
                print(f"BM25 initialized with {len(docs)} local mirror documents.")
        except Exception as e:
            print(f"Failed to initialize BM25 fallback: {e}")


    def search(self, query: str, k: int = 5):
        # 1. Vector Search
        vector_docs = vector_service.similarity_search_with_threshold(query, k=k)
        
        # 2. BM25 Search (if initialized)
        bm25_docs = []
        if self.bm25:
            tokenized_query = query.lower().split()
            bm25_docs = self.bm25.get_top_n(tokenized_query, self.documents, n=k)
        
        # 3. Combine and Deduplicate
        seen = set()
        combined_docs = []
        for doc in vector_docs + bm25_docs:
            key = doc.metadata.get("id") or (doc.metadata.get("source_url", "") + "::" + doc.page_content[:80])
            if key not in seen:
                seen.add(key)
                combined_docs.append(doc)
        return combined_docs[:k]

hybrid_search_service = HybridSearchService()

