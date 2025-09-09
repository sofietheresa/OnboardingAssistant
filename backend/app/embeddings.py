# app/embeddings.py
from typing import List
import os, httpx, json
from .ibm_auth import get_iam_token_manager

API_VERSION = os.environ.get("WATSONX_API_VERSION", "2024-05-01")

class WatsonxAIEmbeddings:
    def __init__(self):
        self.base_url = os.environ["WATSONX_BASE_URL"].rstrip("/")
        self.model_id = os.environ["EMBEDDINGS_MODEL_ID"]
        self.project_id = os.environ.get("WATSONX_PROJECT_ID", "")
        self.timeout = 60

    async def embed(self, texts: List[str]) -> List[List[float]]:
        token_manager = get_iam_token_manager()
        token = await token_manager.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "model_id": self.model_id,
            # WICHTIG: 'inputs' (Plural)
            "inputs": texts,
        }
        if self.project_id:
            payload["project_id"] = self.project_id

        url = f"{self.base_url}/ml/v1/text/embeddings?version={API_VERSION}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code >= 400:
                raise RuntimeError(f"Embeddings error {r.status_code}: {r.text}")

            j = r.json()

            # ---- verschiedene mögliche Antwortformen robust behandeln ----
            # Form 1: {"data":[{"embedding":[...]} , ...]}
            if isinstance(j, dict) and "data" in j:
                out = []
                for item in j["data"]:
                    emb = item.get("embedding") or item.get("values")
                    if emb is None:
                        raise RuntimeError(f"Embeddings response item missing 'embedding/values': {json.dumps(item)[:500]}")
                    out.append(emb)
                return out

            # Form 2: {"results":[{"embedding":[...]} , ...]}
            if isinstance(j, dict) and "results" in j:
                out = []
                for item in j["results"]:
                    emb = item.get("embedding") or item.get("values")
                    if emb is None and "data" in item and isinstance(item["data"], list):
                        # manche Antworten verschachteln es unter item["data"][0]["embedding"]
                        maybe = item["data"][0] if item["data"] else {}
                        emb = maybe.get("embedding") or maybe.get("values")
                    if emb is None:
                        raise RuntimeError(f"Embeddings response item missing 'embedding/values': {json.dumps(item)[:500]}")
                    out.append(emb)
                return out

            # Form 3: {"embeddings":[[...], [...]]}
            if isinstance(j, dict) and "embeddings" in j and isinstance(j["embeddings"], list):
                return j["embeddings"]

            # Wenn wir hier sind, kennen wir das Format nicht:
            raise RuntimeError(f"Unexpected embeddings response format: {json.dumps(j)[:800]}")
