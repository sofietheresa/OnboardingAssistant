import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# RAG-Module
from app.schemas import AskRequest, AskResponse
from app.rag import answer as rag_answer
from app.speech_to_text import get_speech_to_text_service
from app.text_to_speech import get_text_to_speech_service

app = FastAPI(title="Boardy Onboarding Assistant API")

# ---- CORS ----
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8000,"
    "https://boardy-frontend-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud",
)
allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],            
    max_age=600,                   
)

# ---- React Frontend ----
frontend_path = Path("/app/frontend/build")
if frontend_path.exists():
    assets_dir = frontend_path / "assets"
    static_dir = frontend_path / "static"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ---- Datenmodelle ----
class Location(BaseModel):
    id: str
    name: str
    description: str

class SpeechToTextRequest(BaseModel):
    audio_data: str  # Base64-encoded audio data
    content_type: str = "audio/wav"

class SpeechToTextResponse(BaseModel):
    transcript: str
    confidence: float

class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "de-DE_BirgitVoice"

# ---- Health Endpoints ----
@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "Boardy Onboarding Assistant"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "api": "Boardy API"}

# ---- Locations ----
@app.get("/api/locations", response_model=list[Location])
async def list_locations():
    return [
        Location(id="boeblingen", name="IBM Böblingen", description="Entwicklungs- und Innovationszentrum."),
        Location(id="muenchen", name="IBM München", description="Client Center und Lab Standorte."),
        Location(id="ludwigsburg", name="UDG Ludwigsburg", description="Digitalagentur im IBM iX Netzwerk."),
    ]


# ---- Chat über RAG (neuer Endpoint) ----
@app.post("/v1/ask", response_model=AskResponse)
async def ask_rag(req: AskRequest):
    result = await rag_answer(req.query, req.location, req.chatHistory)
    return AskResponse(**result)

# ---- Speech to Text Endpoint ----
@app.post("/api/speech-to-text")
async def speech_to_text(req: SpeechToTextRequest):
    import base64
    
    try:
        # Base64-Daten dekodieren
        audio_data = base64.b64decode(req.audio_data)
        
        # Speech to Text Service
        speech_service = get_speech_to_text_service()
        transcript = await speech_service.transcribe_audio(audio_data, req.content_type)
        
        return {
            'transcript': transcript,
            'confidence': 1.0,  # Confidence wird in speech_to_text.py nicht zurückgegeben
            'success': True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech to Text Fehler: {str(e)}")

# ---- Text to Speech Endpoint ----
@app.post("/api/text-to-speech")
async def text_to_speech(req: TextToSpeechRequest):
    from fastapi.responses import Response
    
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

# ---- Frontend ausliefern ----
@app.get("/")
async def serve_frontend():
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not found", "path": str(frontend_path)}

@app.get("/{path:path}")
async def serve_static(path: str):
    file_path = frontend_path / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=bool(os.getenv("RELOAD", "")),
    )
