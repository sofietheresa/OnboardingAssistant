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
            
            self.token_manager = get_iam_token_manager()
            self.watsonx_url = settings.watsonx_url
            self.project_id = settings.watsonx_project_id
            self.available = True
            logger.info("WatsonX embeddings initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WatsonX embeddings: {e}")
            self.available = False
    
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
            import httpx
            import json
            
            headers = {
                "Authorization": f"Bearer {token_manager.get_token()}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": texts,
                "model_id": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "project_id": self.project_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.watsonx_url}/ml/v1/text/embeddings",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embeddings = [item["embedding"] for item in result["results"]]
                    return embeddings
                else:
                    logger.error(f"WatsonX embeddings failed: {response.status_code} - {response.text}")
                    raise Exception(f"WatsonX API error: {response.status_code}")
                    
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