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

app = FastAPI(title="Boardy Onboarding Assistant API")

# ---- CORS ----
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8000,https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud",
)
allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        port=int(os.getenv("PORT", "8000")),
        reload=bool(os.getenv("RELOAD", "")),
    )
