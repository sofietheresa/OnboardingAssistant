
# app/llm.py
import os, httpx
import logging
from .ibm_auth import iam_token_manager

logger = logging.getLogger(__name__)

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
        
        logger.info("=== LLM REQUEST ===")
        logger.info(f"System Prompt: {system_prompt[:200]}...")
        logger.info(f"User Prompt: {user_prompt[:200]}...")
        logger.info(f"Full Prompt Length: {len(prompt)} characters")

        token = os.environ.get("WATSONX_IAM_TOKEN")
        if not token:
            logger.debug("No IAM token in environment, fetching new one")
            from .ibm_auth import iam_token_manager
            token = await iam_token_manager.get_token()

        headers = {
            "Authorization": f"Bearer {token[:20]}...",  # Masked for logging
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

        logger.info(f"Model ID: {self.model_id}")
        logger.info(f"Project ID: {self.project_id}")
        logger.info(f"Parameters: {payload['parameters']}")
        
        url = f"{self.base_url}/ml/v1/text/generation?version={API_VERSION}"
        logger.info(f"Request URL: {url}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.info("Sending request to WatsonX...")
            r = await client.post(url, headers=headers, json=payload)
            
            logger.info(f"Response Status: {r.status_code}")
            logger.info(f"Response Headers: {dict(r.headers)}")
            
            if r.status_code >= 400:
                logger.error(f"LLM error {r.status_code}: {r.text}")
                raise RuntimeError(f"LLM error {r.status_code}: {r.text}")
            
            data = r.json()
            logger.info("=== LLM RESPONSE ===")
            logger.info(f"Response Data Keys: {list(data.keys())}")
            
            if "results" in data and len(data["results"]) > 0:
                generated_text = data["results"][0]["generated_text"]
                logger.info(f"Generated Text Length: {len(generated_text)} characters")
                logger.info(f"Generated Text Preview: {generated_text[:300]}...")
                logger.info("=== END LLM REQUEST/RESPONSE ===")
                return generated_text
            else:
                logger.error(f"Unexpected response format: {data}")
                raise RuntimeError(f"Unexpected response format: {data}")