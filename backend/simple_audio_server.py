#!/usr/bin/env python3
"""
Einfacher Audio-Server ohne .env Abhängigkeit
"""

import os
import base64
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

# Environment-Variablen direkt setzen (falls nicht bereits gesetzt)
if not os.getenv('SPEECH_TO_TEXT_API_KEY'):
    print("⚠️  SPEECH_TO_TEXT_API_KEY nicht gefunden - verwende WATSONX_API_KEY")
if not os.getenv('TEXT_TO_SPEECH_API_KEY'):
    print("⚠️  TEXT_TO_SPEECH_API_KEY nicht gefunden - verwende WATSONX_API_KEY")

# Audio-Services importieren
from app.speech_to_text import get_speech_to_text_service
from app.text_to_speech import get_text_to_speech_service

app = FastAPI(title="Boardy Audio Services API")

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Datenmodelle ----
class SpeechToTextRequest(BaseModel):
    audio_data: str  # Base64-encoded audio data
    content_type: str = "audio/wav"

class SpeechToTextResponse(BaseModel):
    transcript: str
    confidence: float
    success: bool

class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "de-DE_BirgitVoice"

# ---- Health Endpoints ----
@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "Boardy Audio Services"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "api": "Audio API"}

# ---- Speech to Text Endpoint ----
@app.post("/api/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(req: SpeechToTextRequest):
    try:
        # Base64-Daten dekodieren
        audio_data = base64.b64decode(req.audio_data)
        
        # Speech to Text Service
        speech_service = get_speech_to_text_service()
        transcript = await speech_service.transcribe_audio(audio_data, req.content_type)
        
        return SpeechToTextResponse(
            transcript=transcript,
            confidence=1.0,
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech to Text Fehler: {str(e)}")

# ---- Text to Speech Endpoint ----
@app.post("/api/text-to-speech")
async def text_to_speech(req: TextToSpeechRequest):
    try:
        # Text to Speech Service verwenden
        tts_service = get_text_to_speech_service()
        audio_data = await tts_service.synthesize_text(req.text, req.voice)
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=speech.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text to Speech Fehler: {str(e)}")

# ---- Verfügbare Stimmen ----
@app.get("/api/text-to-speech/voices")
async def get_voices():
    try:
        tts_service = get_text_to_speech_service()
        voices = tts_service.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Stimmen: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starte Boardy Audio Services...")
    print("🎤 Speech-to-Text: Verfügbar")
    print("🔊 Text-to-Speech: Verfügbar")
    print("🌐 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_audio_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
