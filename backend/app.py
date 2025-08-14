import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


app = FastAPI(title="Boardy Onboarding Assistant API")

# CORS for local dev and container access
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000,https://localhost:5173")
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React frontend
frontend_path = Path("/app/frontend/build")
if frontend_path.exists():
    # Mount only directories that actually exist
    assets_dir = frontend_path / "assets"
    static_dir = frontend_path / "static"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class ChatRequest(BaseModel):
    message: str
    model: str = "llama-3-8b"
    location: str = ""

class ChatResponse(BaseModel):
    response: str
    model: str
    location: str

class Location(BaseModel):
    id: str
    name: str
    description: str

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Boardy Onboarding Assistant"}

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {"status": "healthy", "api": "Boardy API"}

@app.get("/api/locations", response_model=list[Location])
async def list_locations():
    """Return available onboarding locations for the UI."""
    return [
        Location(id="boeblingen", name="IBM Böblingen", description="Entwicklungs- und Innovationszentrum."),
        Location(id="muenchen", name="IBM München", description="Client Center und Lab Standorte."),
        Location(id="ludwigsburg", name="UDG Ludwigsburg", description="Digitalagentur im IBM iX Netzwerk."),
    ]

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint that forwards messages to LiteLLM"""
    try:
        # Get LiteLLM URL from environment
        litellm_url = os.getenv("LITELLM_URL", "http://localhost:4000")
        default_model = os.getenv("DEFAULT_MODEL", request.model or "llama-3-8b")
        
        # Prepare the message with location context
        system_message = f"""Du bist Boardy, ein freundlicher Onboarding-Assistent für IBM-Standorte. 
        Der Benutzer befindet sich am Standort: {request.location}
        
        Hilf dem Benutzer bei allen Fragen rund um den Standort, IBM-Produkte, Prozesse und das Onboarding.
        Sei freundlich, hilfsbereit und professionell. Antworte auf Deutsch."""
        
        # Forward to LiteLLM
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{litellm_url}/chat/completions",
                json={
                    "model": default_model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": request.message}
                    ],
                    "stream": False
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]
                
                return ChatResponse(
                    response=assistant_message,
                    model=default_model,
                    location=request.location
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="LiteLLM request failed")
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"LiteLLM service unavailable: {str(e)}")
    except Exception as e:
        # Fallback: return a graceful message so UI can continue in dev
        return ChatResponse(
            response=f"(Lokaler Fallback) Ich habe deine Nachricht erhalten: '{request.message}'. Der LLM-Dienst ist aktuell nicht verfügbar.",
            model=default_model if 'default_model' in locals() else request.model,
            location=request.location,
        )

@app.get("/")
async def serve_frontend():
    """Serve the React frontend"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return {"message": "Frontend not found", "path": str(frontend_path)}

@app.get("/{path:path}")
async def serve_static(path: str):
    """Serve static files from React build"""
    file_path = frontend_path / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    
    # For client-side routing, serve index.html
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=bool(os.getenv("RELOAD", "")),
    )

