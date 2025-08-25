# app/llm.py
import os, httpx
from .ibm_auth import iam_token_manager

class WatsonxAILLM:
    def __init__(self):
        self.base_url = os.environ["WATSONX_BASE_URL"].rstrip("/")
        self.model_id = os.environ["LLM_MODEL_ID"]
        self.project_id = os.environ.get("WATSONX_PROJECT_ID", "")
        self.timeout = 60

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        token = await iam_token_manager.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model_id": self.model_id,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # "parameters": {"temperature": 0.2, "max_new_tokens": 512},
            # "project_id": self.project_id,
        }
        url = f"{self.base_url}/ml/v1/text/generate"  # Region-spezifisch prüfen
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["results"][0]["generated_text"]
