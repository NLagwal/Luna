import time
from langchain_community.chat_message_histories import ChatMessageHistory
from src.core.config import settings

class MemoryService:
    def __init__(self):
        self.sessions = {}
        self.session_data = {}
        self.last_accessed = {}

    def _cleanup_expired(self):
        now = time.time()
        expired_sessions = [
            sid for sid, last_time in self.last_accessed.items()
            if now - last_time > settings.SESSION_TTL
        ]
        for sid in expired_sessions:
            self.sessions.pop(sid, None)
            self.session_data.pop(sid, None)
            self.last_accessed.pop(sid, None)

    def get_session_history(self, session_id: str):
        self._cleanup_expired()
        self.last_accessed[session_id] = time.time()
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatMessageHistory()
        return self.sessions[session_id]

    def get_session_context(self, session_id: str) -> dict:
        self._cleanup_expired()
        return self.session_data.get(session_id, {})

    def set_session_context(self, session_id: str, key: str, value):
        self._cleanup_expired()
        if session_id not in self.session_data:
            self.session_data[session_id] = {}
        self.session_data[session_id][key] = value

    def clear_session(self, session_id: str):
        self.sessions.pop(session_id, None)
        self.session_data.pop(session_id, None)
        self.last_accessed.pop(session_id, None)

memory_service = MemoryService()

