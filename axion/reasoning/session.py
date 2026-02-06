from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str
    content: str

class ConversationSession(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.messages.append(ChatMessage(role=role, content=content))

    def get_messages_dict(self) -> List[Dict[str, str]]:
        return [m.model_dump() for m in self.messages]
