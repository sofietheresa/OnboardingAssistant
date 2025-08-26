# app/llm.py
import os, httpx
from .ibm_auth import iam_token_manager


API_VERSION = os.environ.get("WATSONX_API_VERSION", "2024-05-01")

class WatsonxAILLM:
    def __init__(self):
        self.base_url = os.environ["WATSONX_BASE_URL"].rstrip("/")
        self.model_id = os.environ["LLM_MODEL_ID"]
        self.project_id = os.environ.get("WATSONX_PROJECT_ID", "")
        self.timeout = 60

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # watsonx.ai Text-API erwartet einen Prompt-String
        prompt = f"{system_prompt}\n\n{user_prompt}"

        token = os.environ.get("WATSONX_IAM_TOKEN")
        if not token:
            
            from .ibm_auth import iam_token_manager
            token = await iam_token_manager.get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "model_id": self.model_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",   # oder "sample"
                "max_new_tokens": 512,
                "temperature": 0.2,            # bei "sample" relevant
                "top_p": 1
            },
        }
        if self.project_id:
            payload["project_id"] = self.project_id

        
        url = f"{self.base_url}/ml/v1/text/generation?version={API_VERSION}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code >= 400:
                raise RuntimeError(f"LLM error {r.status_code}: {r.text}")
            data = r.json()
            # übliches Format: {"results":[{"generated_text":"..."}]}
            return data["results"][0]["generated_text"]
