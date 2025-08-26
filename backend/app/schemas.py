from pydantic import BaseModel
from typing import List, Optional

class AskRequest(BaseModel):
    query: str
    user: Optional[dict] = None  # für spätere Personalisierung

class Source(BaseModel):
    title: str
    doc_id: str
    chunk_id: int

class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
