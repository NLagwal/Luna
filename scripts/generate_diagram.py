import base64
import requests
import os
import sys

def generate_mermaid_image(mermaid_code, output_path):
    """Generates an image from Mermaid code using the mermaid.ink API."""
    graphbytes = mermaid_code.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    url = "https://mermaid.ink/img/" + base64_string
    
    print(f"Generating image from: {url}")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Image successfully saved to: {output_path}")
        else:
            print(f"Failed to generate image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_diagram.py <output_file>")
        sys.exit(1)
        
    output_file = sys.argv[1]
    
    # Default architecture diagram
    mermaid_code = """
graph TD
    User((User)) <--> Widget[Luna Chat Widget]
    Widget <--> API[FastAPI Backend]
    
    subgraph "Core Logic"
        API <--> Router{Intent Router}
        Router -- Chitchat --> CC[Instant Response]
        Router -- RAG --> Pipeline[RAG Pipeline]
    end
    
    subgraph "Knowledge Retrieval"
        Pipeline <--> DB[(PostgreSQL)]
        Pipeline <--> Hybrid[Hybrid Search]
        Hybrid <--> Chroma[(ChromaDB)]
        Hybrid <--> BM25[BM25 Index]
    end
    
    subgraph "AI Generation"
        Pipeline <--> Memory[Conversational Memory]
        Pipeline <--> LLM[Ollama / Gemma 4]
    end
    
    DB --- Staff[Faculty & Admin Staff]
    DB --- Facts[Official Fact Registry]
    Chroma --- Vault[Curated PDF Vault]
    Chroma --- Mirror[Website HTML Mirror]
    """
    
    generate_mermaid_image(mermaid_code, output_file)
