from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from enum import Enum

class SearchMethod(str, Enum):
    FILE_UPLOAD = "file_upload"
    IMAGE_URL = "image_url"

class ImageSearchRequest(BaseModel):
    image_url: HttpUrl
    min_similarity: Optional[float] = 0.0
    max_results: Optional[int] = 10

class ProductResult(BaseModel):
    product_id: str
    product_name: str
    category: str
    image_path: str
    similarity_score: float

class SearchResponse(BaseModel):
    query_method: SearchMethod
    total_results: int
    results: List[ProductResult]
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    message: str
    database_loaded: bool
    total_products: int

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[str] = None
