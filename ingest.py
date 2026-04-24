import os
import glob
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import chromadb

# Config
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
EMBED_MODEL = "embeddinggemma:latest"
COLLECTION_NAME = "juit_knowledge_base"
BASE_URL = "https://www.juit.ac.in/"
ROOT_DIR = "/home/lag/Projekt/Luna/"
PARSED_DIR = os.path.join(ROOT_DIR, "PARSED_SHIT")
SCRAPED_DIR = os.path.join(ROOT_DIR, "www.juit.ac.in")

def get_source_url(file_path):
    """Convert local file path to JUIT URL."""
    if "PARSED_SHIT" in file_path:
        rel_path = os.path.relpath(file_path, PARSED_DIR)
        return BASE_URL + rel_path
    elif "www.juit.ac.in" in file_path:
        rel_path = os.path.relpath(file_path, SCRAPED_DIR)
        return BASE_URL + rel_path
    return file_path

def ingest_data():
    print("Initializing ChromaDB connection...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    
    # Initialize Persistent Client
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    # Clear existing collection if it exists
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass
        
    vector_store = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, 
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""]
    )
    all_docs = []

    # 0. Process Hand-Curated Facts (juit_facts.json)
    print("Processing juit_facts.json...")
    import json
    try:
        with open("juit_facts.json", "r") as f:
            facts = json.load(f)
            for key, value in facts.items():
                content = f"{key.upper()}: {value['verbose']}\nSummary: {value['text']}"
                from langchain_core.documents import Document
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "juit_facts.json",
                        "source_url": value.get("ref", BASE_URL),
                        "type": "fact"
                    }
                )
                all_docs.append(doc)
    except Exception as e:
        print(f"Error loading juit_facts.json: {e}")

    # 1. Process Parsed Text (from PARSED_SHIT)
    print("Parsing text files from PARSED_SHIT...")
    text_files = glob.glob(os.path.join(PARSED_DIR, "**/*.txt"), recursive=True)
    
    for file in text_files:
        try:
            # Source URL handling for .txt files (remove the .txt suffix)
            original_file = file.replace(".txt", "")
            source_url = get_source_url(original_file)
            
            loader = TextLoader(file, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_url"] = source_url
            all_docs.extend(text_splitter.split_documents(docs))
        except Exception as e:
            print(f"Error loading {file}: {e}")

    # 2. Process High-Utility PDFs (Fees, Faculty, Admissions, etc.)
    print("Parsing high-utility PDFs...")
    pdf_patterns = [
        "*calendar*.pdf", 
        "*syllabus*.pdf", 
        "*notice*.pdf", 
        "*fee*.pdf", 
        "*admission*.pdf", 
        "*faculty*.pdf", 
        "*prospectus*.pdf", 
        "*placement*.pdf",
        "*Staff*.pdf",
        "*Employee*.pdf",
        "*Form_2026*.pdf",
        "*Procedure_2026*.pdf",
        "ADMISSION_DISCLOSURE*.pdf"
    ]
    
    selected_pdfs = []
    for pattern in pdf_patterns:
        selected_pdfs.extend(glob.glob(os.path.join(SCRAPED_DIR, "**/" + pattern), recursive=True))
    
    # Also specifically look for recent years in any PDF
    recent_pdfs = glob.glob(os.path.join(SCRAPED_DIR, "**/*202[5-7]*.pdf"), recursive=True)
    selected_pdfs.extend(recent_pdfs)
    
    # Use a set to avoid duplicates
    selected_pdfs = list(set(selected_pdfs))
    
    # Sort to prioritize recent years (string sort will put 2026 after 2025)
    selected_pdfs.sort(key=lambda x: ("2026" in x or "2027" in x), reverse=True)
    
    # Reasonable limit for performance (e.g., 500)
    selected_pdfs = selected_pdfs[:500] 
    
    for pdf in selected_pdfs:
        try:
            loader = PyMuPDFLoader(pdf)
            docs = loader.load()
            for doc in docs:
                # Add source URL and ensure metadata is correct
                doc.metadata["source_url"] = get_source_url(pdf)
            all_docs.extend(text_splitter.split_documents(docs))
            print(f"Indexed PDF: {pdf}")
        except Exception as e:
            print(f"Error loading PDF {pdf}: {e}")

    print(f"Total chunks created: {len(all_docs)}")
    
    # Batch add to vector store
    batch_size = 100
    for i in range(0, len(all_docs), batch_size):
        batch = all_docs[i:i+batch_size]
        vector_store.add_documents(batch)
        print(f"Added batch {i//batch_size + 1}/{(len(all_docs)//batch_size)+1}", flush=True)

    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_data()
