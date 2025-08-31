import os
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
import io
from typing import List, Dict, Any, Optional
import json
from pinecone import Pinecone, ServerlessSpec
import logging

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        self.pc = None
        self.index = None
        self.model = None
        self.index_name = "visual-product-matcher"
        
    async def initialize(self):
        """Initialize Pinecone connection and load embedding model"""
        try:
            # Initialize Pinecone
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY environment variable is required")
            
            self.pc = Pinecone(api_key=api_key)
            
            # Create index if it doesn't exist
            if self.index_name not in [index.name for index in self.pc.list_indexes()]:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=512,  # MobileNetV2 feature dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            self.index = self.pc.Index(self.index_name)
            
            # Load pre-trained model for better embeddings
            logger.info("Loading MobileNetV2 model...")
            self.model = hub.load("https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/5")
            
            logger.info("Pinecone service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone service: {e}")
            return False
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Preprocess image for MobileNetV2"""
        try:
            # Open and preprocess image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to 224x224 (MobileNetV2 input size)
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            
            # Convert to numpy array and normalize
            image_array = np.array(image, dtype=np.float32)
            image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
            image_array = image_array / 255.0  # Normalize to [0, 1]
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def generate_embedding(self, image_data: bytes) -> Optional[List[float]]:
        """Generate embedding using MobileNetV2"""
        try:
            if self.model is None:
                logger.error("Model not initialized")
                return None
            
            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            
            # Generate embedding
            embedding = self.model(processed_image)
            embedding_list = embedding.numpy().flatten().tolist()
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def upsert_products(self, products: List[Dict[str, Any]]):
        """Upsert product embeddings to Pinecone"""
        try:
            if not self.index:
                raise ValueError("Pinecone index not initialized")
            
            vectors = []
            for product in products:
                if 'embedding' in product and product['embedding']:
                    vector_data = {
                        'id': product['product_id'],
                        'values': product['embedding'],
                        'metadata': {
                            'product_name': product['product_name'],
                            'category': product['category'],
                            'image_path': product['image_path']
                        }
                    }
                    vectors.append(vector_data)
            
            if vectors:
                # Upsert in batches of 100
                batch_size = 100
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                    logger.info(f"Upserted batch {i//batch_size + 1} of {len(batch)} vectors")
                
                logger.info(f"Successfully upserted {len(vectors)} product embeddings")
            
        except Exception as e:
            logger.error(f"Error upserting products to Pinecone: {e}")
            raise
    
    async def search_similar(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar products using Pinecone"""
        try:
            if not self.index:
                raise ValueError("Pinecone index not initialized")
            
            # Query Pinecone
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            results = []
            for match in response.matches:
                result = {
                    'product_id': match.id,
                    'product_name': match.metadata.get('product_name', ''),
                    'category': match.metadata.get('category', ''),
                    'image_path': match.metadata.get('image_path', ''),
                    'similarity_score': float(match.score)
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar products: {e}")
            return []
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        try:
            if not self.index:
                return {"error": "Index not initialized"}
            
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "index_fullness": stats.index_fullness
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"error": str(e)}

# Global instance
pinecone_service = PineconeService()
