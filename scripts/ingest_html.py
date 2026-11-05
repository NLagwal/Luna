import os
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.services.vector import vector_service
from src.core.config import settings

def ingest_html_mirror(mirror_dir):
    print(f"Scanning mirror directory: {mirror_dir}...")
    documents = []
    
    for root, dirs, files in os.walk(mirror_dir):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        soup = BeautifulSoup(f, "html.parser")
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                            
                        text = soup.get_text(separator=" ")
                        # Clean whitespace
                        clean_text = " ".join(text.split())
                        
                        if len(clean_text) > 200:
                            # Try to construct a source URL from path
                            rel_path = os.path.relpath(path, mirror_dir)
                            source_url = f"https://{rel_path.replace('.html', '')}" # Simplified
                            
                            documents.append(Document(
                                page_content=clean_text,
                                metadata={"source_url": source_url, "path": path}
                            ))
                except Exception as e:
                    print(f"Error parsing {path}: {e}")

    if not documents:
        print("No valid HTML files found.")
        return

    print(f"Splitting {len(documents)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    print(f"Adding {len(texts)} chunks to ChromaDB collection '{settings.COLLECTION_NAME}'...")
    # Process in batches to avoid overwhelming the system
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        vector_service.vector_store.add_documents(batch)
        print(f"Indexed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

    print("HTML Ingestion complete.")

if __name__ == "__main__":
    mirror_path = os.path.join(settings.ROOT_DIR, "www.juit.ac.in")
    if os.path.exists(mirror_path):
        ingest_html_mirror(mirror_path)
    else:
        print(f"Mirror directory not found at {mirror_path}")
