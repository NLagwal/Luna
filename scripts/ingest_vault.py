import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.services.vector import vector_service
from src.core.config import settings

def ingest_vault(vault_dir):
    print(f"Loading documents from {vault_dir}...")
    loader = DirectoryLoader(vault_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    print(f"Splitting {len(documents)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    print(f"Adding {len(texts)} chunks to ChromaDB collection '{settings.COLLECTION_NAME}'...")
    vector_service.vector_store.add_documents(texts)
    print("Ingestion complete.")

if __name__ == "__main__":
    # Create a vault directory if it doesn't exist
    vault_path = os.path.join(settings.ROOT_DIR, "vault")
    if not os.path.exists(vault_path):
        os.makedirs(vault_path)
        print(f"Created {vault_path}. Please place critical PDFs there.")
    else:
        ingest_vault(vault_path)
