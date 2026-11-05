import string

class IntentRouter:
    CHITCHAT_KEYWORDS = ["hello", "hi", "hey", "who are you", "what can you do", "thanks", "thank you"]
    
    @classmethod
    def _clean_query(cls, query: str) -> str:
        query_lower = query.lower().strip()
        # Remove punctuation for matching
        cleaned = query_lower.translate(str.maketrans('', '', string.punctuation)).strip()
        return " ".join(cleaned.split())

    @classmethod
    def classify(cls, query: str):
        clean_q = cls._clean_query(query)
        
        # 1. Chitchat Check
        if any(word == clean_q for word in cls.CHITCHAT_KEYWORDS) or \
           any(clean_q.startswith(word + " ") for word in cls.CHITCHAT_KEYWORDS):
            return "chitchat"
        
        return "rag"

    @classmethod
    def get_chitchat_response(cls, query: str):
        clean_q = cls._clean_query(query)
        if any(w in clean_q.split() for w in ["hello", "hi", "hey"]):
            return "Hello! I am Luna, your JUIT AI assistant. How can I help you today?"
        if "who are you" in clean_q or "what can you do" in clean_q:
            return "I am Luna, the official senior AI assistant for Jaypee University of Information Technology (JUIT). I can help you with faculty profiles, admission details, fee structures, and more."
        if "thanks" in clean_q or "thank you" in clean_q:
            return "You're welcome! Feel free to ask if you have more questions."
        return "I'm here to help with any JUIT-related inquiries!"

