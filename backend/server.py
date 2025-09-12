import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil

# RAG-Module
from app.schemas import AskRequest, AskResponse, SpeechToTextRequest, TextToSpeechRequest
from app.rag import answer as rag_answer

from app.speech_to_text import get_speech_to_text_service
from app.text_to_speech import get_text_to_speech_service

app = FastAPI(title="Boardy Onboarding Assistant API")

UPLOAD_DIR = Path(__file__).parent.parent / "uploaded_files"
UPLOAD_DIR.mkdir(exist_ok=True)

# ---- CORS ----
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8080,"
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
    result = await rag_answer(req.query)
    return AskResponse(**result)


# ---- Speech to Text Endpoint ----
@app.options("/api/speech-to-text")
async def speech_to_text_options():
    return {"message": "OK"}

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


# ---- File Upload Endpoint ----
@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload fehlgeschlagen: {str(e)}")

@app.post("/api/ask-with-file")
async def ask_with_file(query: str = Form(...), file: UploadFile = File(...)):
    """
    Nutzt den Inhalt der hochgeladenen Datei als temporären Kontext für die aktuelle Frage,
    ohne sie ins RAG aufzunehmen.
    """
    import tempfile
    from ingest.loaders import load_documents
    from ingest.chunker import split_into_chunks, to_records
    from app.rag import answer as rag_answer

    # Datei temporär speichern
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)  # Ensure tmp_path is a Path object

    # Dokument laden und in Chunks splitten
    print(f"[DEBUG] ask-with-file: tmp_path={tmp_path}, suffix={tmp_path.suffix}, exists={tmp_path.exists()}")
    docs = list(load_documents([tmp_path]))
    print(f"[DEBUG] ask-with-file: docs loaded: {len(docs)}")
    if not docs:
        raise HTTPException(status_code=400, detail=f"Datei konnte nicht verarbeitet werden. Unterstützte Dateitypen: .pdf, .docx, .md, .markdown. Übergeben: {tmp_path.name}")
    chunks = split_into_chunks(docs[0]["text"])
    records = to_records("temp_doc", chunks, docs[0]["metadata"])

    # Kontext für diese Anfrage zusammenbauen
    context_texts = [r["content"] for r in records]
    context = "\n\n".join(context_texts[:8])
    # Prompt bauen wie in rag.py
    prompt = (
        f"FRAGE:\n{query}\n\n"
        f"KONTEXT (verwende NUR Folgendes):\n{context}\n\n"
        "ANTWORTFORMAT:\n- knappe Antwort in Deutsch\n- bei Prozessen: nummerierte Schritte\n- Abschlusszeile: 'Quellen: <Datei>'\n"
    )
    # LLM aufrufen
    result = await rag_answer(prompt)
    return result


@app.post("/api/ingest-uploaded-file")
async def ingest_uploaded_file(filename: str = Form(...)):
    import subprocess
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    # Lege temporäres Verzeichnis für Ingest an
    import tempfile, shutil as sh
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / filename
        sh.copy(file_path, tmp_file)
        # Starte Ingest-Prozess
        proc = subprocess.run([
            "python", "-m", "ingest.ingest", tmpdir
        ], capture_output=True, text=True)
        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Ingest-Fehler: {proc.stderr}")
    return {"ingested": True, "filename": filename}


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
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        reload=bool(os.getenv("RELOAD", "")),
    )
