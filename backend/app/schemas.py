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

class SpeechToTextRequest(BaseModel):
    audio_data: str  # Base64-encoded audio data
    content_type: str

class TextToSpeechRequest(BaseModel):
    text: str
    voice: Optional[str] = "en-US_AllisonV3Voice"  # Default voice
