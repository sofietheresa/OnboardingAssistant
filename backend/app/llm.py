# app/llm.py
import os
import httpx
import json
from typing import Optional
from .ibm_auth import get_iam_token_manager

API_VERSION = os.environ.get("WATSONX_API_VERSION", "2024-05-01")

class WatsonxAILLM:
    def __init__(self):
        self.base_url = os.environ.get("WATSONX_BASE_URL", "").rstrip("/")
        self.model_id = os.environ.get("WATSONX_MODEL_ID", "meta-llama/llama-3.1-8b-instruct")
        self.project_id = os.environ.get("WATSONX_PROJECT_ID", "")
        self.timeout = 60
        
        if not self.base_url:
            raise ValueError("WATSONX_BASE_URL environment variable is required")

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using Watsonx AI LLM"""
        try:
            token_manager = get_iam_token_manager()
            token = await token_manager.get_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            payload = {
                "model_id": self.model_id,
                "input": user_prompt,
                "system": system_prompt,
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                }
            }
            
            if self.project_id:
                payload["project_id"] = self.project_id

            url = f"{self.base_url}/ml/v1/text/generation?version={API_VERSION}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code >= 400:
                    raise RuntimeError(f"LLM error {response.status_code}: {response.text}")

                result = response.json()
                
                # Extract generated text from response
                if "results" in result and len(result["results"]) > 0:
                    generated_text = result["results"][0].get("generated_text", "")
                    return generated_text.strip()
                else:
                    raise RuntimeError(f"Unexpected LLM response format: {json.dumps(result)[:500]}")
                    
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {e}")
