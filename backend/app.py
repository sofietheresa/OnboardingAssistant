import os
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    stream: Optional[bool] = False


app = FastAPI()


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict:
    litellm_url = os.getenv("LITELLM_URL", "http://litellm:4000")
    model_name = request.model or os.getenv("MODEL_NAME", "llama-3-8b")

    payload = {
        "model": model_name,
        "messages": [m.model_dump() for m in request.messages],
        "stream": False,  # keep simple for first cut; extend later
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        try:
            resp = await client.post(f"{litellm_url}/chat/completions", json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"LLM gateway error: {e}")

    data = resp.json()

    # Normalize a minimal response shape for the frontend
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = None

    return {
        "raw": data,
        "model": model_name,
        "message": content,
    }


# Serve static frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=bool(os.getenv("RELOAD", "")),
    )

