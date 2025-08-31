import os
import sys
import json
import time
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from models import (
    ImageSearchRequest, 
    SearchResponse, 
    HealthResponse, 
    ErrorResponse,
    SearchMethod,
    ProductResult
)
from similarity import generate_query_embedding, find_similar_products, get_category_stats
from pinecone_service import pinecone_service

load_dotenv()

app = FastAPI(
    title="Visual Product Matcher API",
    description="Fashion product similarity search",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for now
        "https://visual-product-matcher.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "*",
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
)

product_database: Optional[Dict[str, Any]] = None

# Configure image directory path for different environments  
image_dir = os.getenv("IMAGE_DIRECTORY", "./images")
if Path(image_dir).exists():
    app.mount("/images", StaticFiles(directory=image_dir), name="images")
    print(f"Serving images from {image_dir}")
else:
    print(f"Warning: Image directory {image_dir} not found")
    # Create images directory if it doesn't exist
    Path(image_dir).mkdir(exist_ok=True)
    print(f"Created images directory: {image_dir}")

def load_product_database():
    global product_database
    
    # Try deployment database first (for production), then fallback to full database
    db_paths = ["product_database_deploy.json", "product_database.json"]
    
    for db_path in db_paths:
        if Path(db_path).exists():
            try:
                with open(db_path, 'r') as f:
                    product_database = json.load(f)
                
                products_count = len(product_database.get('products', []))
                print(f"Loaded product database from {db_path} with {products_count} products")
                return True
                
            except Exception as e:
                print(f"Error loading {db_path}: {e}")
                continue
    
    print("No product database found. Please run the data processing scripts first.")
    return False


@app.on_event("startup")
async def startup_event():
    try:
        print("Starting Visual Product Matcher API...")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        
        if not load_product_database():
            raise RuntimeError("Failed to load product database")
        
        print("API ready!")
        
    except Exception as e:
        print(f"Startup error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="healthy",
        message="Visual Product Matcher API is running",
        database_loaded=product_database is not None,
        total_products=len(product_database.get('products', [])) if product_database else 0
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy" if product_database else "unhealthy",
        message="Database loaded successfully" if product_database else "Database not loaded",
        database_loaded=product_database is not None,
        total_products=len(product_database.get('products', [])) if product_database else 0
    )

@app.get("/categories")
async def get_categories():
    if not product_database:
        raise HTTPException(status_code=503, detail="Product database not loaded")
    
    category_stats = get_category_stats(product_database)
    
    return {
        "categories": list(category_stats.keys()),
        "category_counts": category_stats,
        "total_categories": len(category_stats)
    }

@app.post("/api/search/upload", response_model=SearchResponse)
async def search_by_upload(
    file: UploadFile = File(...),
    min_similarity: float = Query(0.0, ge=0.0, le=1.0),
    max_results: int = Query(10, ge=1, le=50),
    use_pinecone: bool = Query(False, description="Use Pinecone vector database for search")
):
    """Search for similar products by uploading an image file"""
    
    if not product_database:
        raise HTTPException(status_code=503, detail="Product database not loaded")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    start_time = time.time()
    
    try:
        # Read image data
        image_data = await file.read()
        
        if use_pinecone and pinecone_service.index:
            # Use Pinecone for similarity search
            query_embedding = pinecone_service.generate_embedding(image_data)
            
            if not query_embedding:
                raise HTTPException(status_code=400, detail="Failed to process image with Pinecone")
            
            similar_products = await pinecone_service.search_similar(query_embedding, max_results)
            
            # Filter by minimum similarity
            similar_products = [p for p in similar_products if p['similarity_score'] >= min_similarity]
        else:
            # Use local similarity search
            query_embedding = generate_query_embedding(image_data)
            
            if not query_embedding:
                raise HTTPException(status_code=400, detail="Failed to process image")
            
            similar_products = find_similar_products(
                query_embedding, 
                product_database, 
                min_similarity, 
                max_results
            )
        
        # Convert to response format
        results = [
            ProductResult(
                product_id=product['product_id'],
                product_name=product['product_name'],
                category=product['category'],
                image_path=product['image_path'],
                similarity_score=product['similarity_score']
            )
            for product in similar_products
        ]
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query_method=SearchMethod.FILE_UPLOAD,
            total_results=len(results),
            results=results,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/search/url", response_model=SearchResponse)
async def search_by_url(
    request: ImageSearchRequest,
    use_pinecone: bool = Query(False, description="Use Pinecone vector database for search")
):
    """Search for similar products by providing an image URL"""
    
    if not product_database:
        raise HTTPException(status_code=503, detail="Product database not loaded")
    
    start_time = time.time()
    
    try:
        # Download image from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(str(request.image_url))
            response.raise_for_status()
            image_data = response.content
        
        if use_pinecone and pinecone_service.index:
            # Use Pinecone for similarity search
            query_embedding = pinecone_service.generate_embedding(image_data)
            
            if not query_embedding:
                raise HTTPException(status_code=400, detail="Failed to process image with Pinecone")
            
            similar_products = await pinecone_service.search_similar(query_embedding, request.max_results)
            
            # Filter by minimum similarity
            similar_products = [p for p in similar_products if p['similarity_score'] >= request.min_similarity]
        else:
            # Use local similarity search
            query_embedding = generate_query_embedding(image_data)
            
            if not query_embedding:
                raise HTTPException(status_code=400, detail="Failed to process image from URL")
            
            similar_products = find_similar_products(
                query_embedding, 
                product_database, 
                request.min_similarity, 
                request.max_results
            )
        
        # Convert to response format
        results = [
            ProductResult(
                product_id=product['product_id'],
                product_name=product['product_name'],
                category=product['category'],
                image_path=product['image_path'],
                similarity_score=product['similarity_score']
            )
            for product in similar_products
        ]
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query_method=SearchMethod.IMAGE_URL,
            total_results=len(results),
            results=results,
            processing_time=processing_time
        )
        
    except httpx.HTTPError:
        raise HTTPException(status_code=400, detail="Failed to download image from URL")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/products/{product_id}")
async def get_product_details(product_id: str):
    """Get details for a specific product"""
    
    if not product_database:
        raise HTTPException(status_code=503, detail="Product database not loaded")
    
    products = product_database.get('products', [])
    
    for product in products:
        if product['product_id'] == product_id:
            return {
                "product_id": product['product_id'],
                "product_name": product['product_name'],
                "category": product['category'],
                "image_path": product['image_path']
            }
    
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/pinecone/stats")
async def get_pinecone_stats():
    """Get Pinecone index statistics"""
    try:
        stats = await pinecone_service.get_index_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Pinecone stats: {str(e)}")

@app.post("/api/pinecone/initialize")
async def initialize_pinecone():
    """Initialize Pinecone service"""
    try:
        success = await pinecone_service.initialize()
        if success:
            return {"message": "Pinecone service initialized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize Pinecone service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing Pinecone: {str(e)}")

# Error handling
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return ErrorResponse(
        error="Not Found",
        message="The requested resource was not found"
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return ErrorResponse(
        error="Internal Server Error",
        message="An unexpected error occurred",
        details=str(exc)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
