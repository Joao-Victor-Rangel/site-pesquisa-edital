import pinecone
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class PineconeClient:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "funding-opportunities")
        
        if not self.api_key or not self.environment:
            logger.warning("Pinecone credentials not found. Vector operations will be disabled.")
            self.enabled = False
            return
            
        try:
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
            
            # Create index if it doesn't exist
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(self.index_name)
            self.enabled = True
            logger.info(f"Pinecone client initialized with index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.enabled = False
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Upsert vectors to Pinecone index"""
        if not self.enabled:
            logger.warning("Pinecone not enabled, skipping vector upsert")
            return False
            
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Successfully upserted {len(vectors)} vectors")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            return False
    
    def query_vectors(
        self, 
        vector: List[float], 
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query similar vectors from Pinecone"""
        if not self.enabled:
            logger.warning("Pinecone not enabled, returning empty results")
            return []
            
        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True
            )
            return results.matches
        except Exception as e:
            logger.error(f"Failed to query vectors: {e}")
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors from Pinecone index"""
        if not self.enabled:
            logger.warning("Pinecone not enabled, skipping vector deletion")
            return False
            
        try:
            self.index.delete(ids=ids)
            logger.info(f"Successfully deleted {len(ids)} vectors")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False

# Global instance
pinecone_client = PineconeClient()