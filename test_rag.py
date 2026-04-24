from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import chromadb

# Config
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
EMBED_MODEL = "embeddinggemma:latest"
LLM_MODEL = "gemma4:e2b"
COLLECTION_NAME = "juit_knowledge_base"

print("Initializing RAG Pipeline for diagnostics...")
embeddings = OllamaEmbeddings(model=EMBED_MODEL)
llm = OllamaLLM(model=LLM_MODEL, timeout=120)

print("Connecting to ChromaDB...")
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
vector_store = Chroma(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

# Template for RAG
prompt_template = """You are Luna, the official AI assistant for Jaypee University of Information Technology (JUIT) Solan. 
Use the following context to answer the user request. 
If you do not know the answer, say so clearly. 

Context:
{context}

Question:
{question}

Answer: """
PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

test_query = "What is the date for National Science Day Symposium 2026?"
print(f"Executing test query: '{test_query}'")
try:
    result = qa_chain.invoke({"query": test_query})
    print("Success!")
    print("Result:", result.get("result"))
    # Also print sources
    print("Sources:", [doc.metadata.get('source_url') for doc in result.get('source_documents', [])])
except Exception as e:
    print("FAILED with exception:")
    import traceback
    traceback.print_exc()
