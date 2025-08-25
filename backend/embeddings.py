# app/embeddings.py
from typing import List
import os, httpx
from .ibm_auth import iam_token_manager

class WatsonxAIEmbeddings:
    def __init__(self):
        self.base_url = os.environ["WATSONX_BASE_URL"].rstrip("/")
        self.model_id = os.environ["EMBEDDINGS_MODEL_ID"]
        self.project_id = os.environ.get("WATSONX_PROJECT_ID", "")
        self.timeout = 60

    async def embed(self, texts: List[str]) -> List[List[float]]:
        token = await iam_token_manager.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model_id": self.model_id,
            "input": texts,
            # "project_id": self.project_id,  # falls benötigt
        }
        url = f"{self.base_url}/ml/v1/text/embeddings"  # Region-spezifisch prüfen
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return [item["embedding"] for item in data["data"]]
