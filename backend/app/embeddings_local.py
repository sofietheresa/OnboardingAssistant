# app/embeddings_local.py
# Local embeddings implementation using sentence-transformers for IBM Cloud deployment

import asyncio
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class LocalEmbeddings:
    """Local embeddings implementation using sentence-transformers"""
    
    def __init__(self):
        self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self.model = None
        self.embedding_dim = 384
        
    async def _load_model(self):
        """Lazy load the model"""
        if self.model is None:
            try:
                logger.info(f"Loading embeddings model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embeddings model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embeddings model: {e}")
                raise RuntimeError(f"Could not load embeddings model: {e}")
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        await self._load_model()
        
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
            logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError(f"Could not generate embeddings: {e}")

# Global instance
_local_embeddings: LocalEmbeddings = None

def get_local_embeddings() -> LocalEmbeddings:
    """Get the global local embeddings instance"""
    global _local_embeddings
    if _local_embeddings is None:
        _local_embeddings = LocalEmbeddings()
    return _local_embeddings
