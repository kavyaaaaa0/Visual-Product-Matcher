# Dummy Pinecone service implementation - no external dependencies
# This allows the app to run without Pinecone/TensorFlow/numpy

from typing import List, Dict, Any, Optional

class PineconeService:
    """Dummy Pinecone service that always returns empty results"""
    
    def __init__(self):
        self.index = None  # Always None to indicate not available
        
    async def initialize(self) -> bool:
        """Dummy initialization that always fails gracefully"""
        print("Pinecone service disabled for deployment")
        return False
    
    def generate_embedding(self, image_data: bytes) -> Optional[List[float]]:
        """Dummy embedding generator that returns None"""
        return None
    
    async def search_similar(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Dummy search that returns empty results"""
        return []
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Dummy stats that returns not available message"""
        return {"error": "Pinecone service not available"}
    
    async def upsert_products(self, products: List[Dict[str, Any]]):
        """Dummy upsert that does nothing"""
        pass

# Global instance
pinecone_service = PineconeService()
