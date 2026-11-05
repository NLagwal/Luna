from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from src.core.config import settings

class LLMService:
    def __init__(self):
        if settings.LLM_PROVIDER in ["local_qwen", "omniroute", "openai", "local_openai", "qwen"]:
            from langchain_openai import ChatOpenAI
            model_name = getattr(settings, "OPENAI_MODEL", None) or getattr(settings, "OMNIROUTE_MODEL", "default")
            self.llm = ChatOpenAI(
                base_url=settings.OPENAI_API_BASE,
                api_key=settings.OPENAI_API_KEY,
                model=model_name,
                temperature=0.0,
                max_tokens=1024,
                timeout=300
            )
        else:
            from langchain_ollama import OllamaLLM
            self.llm = OllamaLLM(model=settings.LLM_MODEL, timeout=120)

        try:
            from langchain_ollama import OllamaEmbeddings
            self.embeddings = OllamaEmbeddings(model=settings.EMBED_MODEL)
        except Exception:
            self.embeddings = None
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Luna, the official senior AI assistant for Jaypee University of Information Technology (JUIT) Solan. 

Your goal is to provide accurate, helpful, and professional answers based ONLY on the 'PROVIDED RECORDS' below.

STRICT RULES:
1. Use ONLY the provided records. No external knowledge.
2. If the info is missing, say: "I do not have that specific information in the official JUIT database."
3. Be concise, direct, and senior in tone. State the direct answer clearly without lengthy thought processes.

PROVIDED RECORDS:
{context}"""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])

    def get_chain(self):
        return self.prompt | self.llm | StrOutputParser()

llm_service = LLMService()

