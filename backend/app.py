import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


app = FastAPI(title="Boardy Onboarding Assistant API")

# Serve React frontend
frontend_path = Path("/app/frontend/build")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

class ChatRequest(BaseModel):
    message: str
    model: str = "llama-3-8b"
    location: str = ""

class ChatResponse(BaseModel):
    response: str
    model: str
    location: str

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Boardy Onboarding Assistant"}

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {"status": "healthy", "api": "Boardy API"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint that forwards messages to LiteLLM"""
    try:
        # Get LiteLLM URL from environment
        litellm_url = os.getenv("LITELLM_URL", "http://localhost:4000")
        
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
                    "model": request.model,
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
                    model=request.model,
                    location=request.location
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="LiteLLM request failed")
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"LiteLLM service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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

