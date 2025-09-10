# app/embeddings.py
# Hybrid embeddings implementation - supports both WatsonX and local embeddings
# Compatible with original merge c11 while providing local fallback

from typing import List, Optional
import os
import asyncio
import logging
from .config import settings

logger = logging.getLogger(__name__)

class WatsonxAIEmbeddings:
    """Hybrid embeddings implementation - WatsonX or local fallback"""
    
    def __init__(self):
        self.use_watsonx = bool(settings.watsonx_api_key and settings.watsonx_api_key != "your_watsonx_api_key_here")
        self.model = None
        self.embedding_dim = 384  # sentence-transformers dimension
        
        if self.use_watsonx:
            logger.info("Using WatsonX embeddings")
            self._init_watsonx()
        else:
            logger.info("Using local sentence-transformers embeddings")
            self._init_local()
    
    def _init_watsonx(self):
        """Initialize WatsonX embeddings (original implementation)"""
        try:
            from .ibm_auth import get_iam_token_manager
            import httpx
            import json
            
            self.base_url = settings.watsonx_base_url.rstrip("/")
            self.model_id = settings.embeddings_model_id
            self.project_id = settings.watsonx_project_id
            self.timeout = 60
            self.api_version = os.environ.get("WATSONX_API_VERSION", "2024-05-01")
            self.get_token = get_iam_token_manager
            self.httpx = httpx
            self.json = json
            
        except ImportError as e:
            logger.warning(f"WatsonX dependencies not available: {e}. Falling back to local embeddings.")
            self.use_watsonx = False
            self._init_local()
    
    def _init_local(self):
        """Initialize local sentence-transformers embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            self.SentenceTransformer = SentenceTransformer
            self.np = np
            
        except ImportError as e:
            logger.error(f"Local embeddings dependencies not available: {e}")
            raise RuntimeError("Neither WatsonX nor local embeddings are available")
    
    async def _load_local_model(self):
        """Lazy load the local model"""
        if self.model is None:
            try:
                logger.info(f"Loading local embeddings model: {self.model_name}")
                self.model = self.SentenceTransformer(self.model_name)
                logger.info("Local embeddings model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load local embeddings model: {e}")
                raise RuntimeError(f"Could not load local embeddings model: {e}")
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts (original interface)"""
        if self.use_watsonx:
            return await self._embed_watsonx(texts)
        else:
            return await self._embed_local(texts)
    
    async def _embed_watsonx(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using WatsonX (original implementation)"""
        try:
            token_manager = self.get_token()
            token = await token_manager.get_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            payload = {
                "model_id": self.model_id,
                # WICHTIG: 'inputs' (Plural) - original implementation
                "inputs": texts,
            }
            if self.project_id:
                payload["project_id"] = self.project_id

            url = f"{self.base_url}/ml/v1/text/embeddings?version={self.api_version}"

            async with self.httpx.AsyncClient(timeout=self.timeout) as client:
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
                            raise RuntimeError(f"Embeddings response item missing 'embedding/values': {self.json.dumps(item)[:500]}")
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
                            raise RuntimeError(f"Embeddings response item missing 'embedding/values': {self.json.dumps(item)[:500]}")
                        out.append(emb)
                    return out

                # Form 3: {"embeddings":[[...], [...]]}
                if isinstance(j, dict) and "embeddings" in j and isinstance(j["embeddings"], list):
                    return j["embeddings"]

                # Wenn wir hier sind, kennen wir das Format nicht:
                raise RuntimeError(f"Unexpected embeddings response format: {self.json.dumps(j)[:800]}")
                    
        except Exception as e:
            logger.warning(f"WatsonX embeddings failed: {e}. Falling back to local embeddings.")
            self.use_watsonx = False
            self._init_local()
            return await self._embed_local(texts)
    
    async def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence-transformers"""
        await self._load_local_model()
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Convert to list of lists
            if len(embeddings.shape) == 1:
                embeddings = [embeddings.tolist()]
            else:
                embeddings = embeddings.tolist()
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate local embeddings: {e}")
            raise RuntimeError(f"Could not generate embeddings: {e}")

# Global instance - lazy initialization (original pattern)
watsonx_ai_embeddings: Optional[WatsonxAIEmbeddings] = None

def get_watsonx_ai_embeddings() -> WatsonxAIEmbeddings:
    """Get the global embeddings instance, creating it if necessary (original interface)"""
    global watsonx_ai_embeddings
    if watsonx_ai_embeddings is None:
        watsonx_ai_embeddings = WatsonxAIEmbeddings()
    return watsonx_ai_embeddings

# Backward compatibility - original global instance
iam_token_manager = None  # Will be set by ibm_auth module