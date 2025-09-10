from pydantic import BaseModel
from typing import List, Optional

class Location(BaseModel):
    id: str
    name: str
    description: str

class Message(BaseModel):
    id: str
    text: str
    isUser: bool
    timestamp: str

class AskRequest(BaseModel):
    query: str
    location: Optional[Location] = None
    chatHistory: Optional[List[Message]] = None
    user: Optional[dict] = None  # für spätere Personalisierung

class Source(BaseModel):
    title: str
    doc_id: str
    chunk_id: int

class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
