#!/usr/bin/env python3
"""
Migration script to:
1. Load existing product database
2. Generate better embeddings using MobileNetV2
3. Upload embeddings to Pinecone
"""

import json
import os
import asyncio
from pathlib import Path
from PIL import Image
import logging
from dotenv import load_dotenv

from pinecone_service import pinecone_service

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_products_to_pinecone():
    """Migrate products from local database to Pinecone"""
    
    # Load product database
    db_path = Path("product_database.json")
    if not db_path.exists():
        logger.error("Product database not found!")
        return False
    
    with open(db_path, 'r') as f:
        product_database = json.load(f)
    
    products = product_database.get('products', [])
    logger.info(f"Found {len(products)} products to migrate")
    
    # Initialize Pinecone service
    if not await pinecone_service.initialize():
        logger.error("Failed to initialize Pinecone service")
        return False
    
    # Process products in batches
    batch_size = 50
    updated_products = []
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}: products {i+1} to {min(i+batch_size, len(products))}")
        
        for product in batch:
            try:
                # Load image
                image_path = product.get('image_path', '')
                if not image_path:
                    continue
                
                # Construct full image path
                full_image_path = Path(f"../data_processing/dataset/Images/Images/{image_path.split('/')[-1]}")
                
                if not full_image_path.exists():
                    logger.warning(f"Image not found: {full_image_path}")
                    continue
                
                # Read image data
                with open(full_image_path, 'rb') as img_file:
                    image_data = img_file.read()
                
                # Generate new embedding
                embedding = pinecone_service.generate_embedding(image_data)
                
                if embedding:
                    # Update product with new embedding
                    updated_product = product.copy()
                    updated_product['embedding'] = embedding
                    updated_products.append(updated_product)
                    logger.info(f"Generated embedding for product {product['product_id']}")
                else:
                    logger.warning(f"Failed to generate embedding for product {product['product_id']}")
                    
            except Exception as e:
                logger.error(f"Error processing product {product.get('product_id', 'unknown')}: {e}")
                continue
    
    # Upload to Pinecone
    if updated_products:
        logger.info(f"Uploading {len(updated_products)} products to Pinecone...")
        await pinecone_service.upsert_products(updated_products)
        
        # Save updated database
        updated_database = {
            'metadata': product_database.get('metadata', {}),
            'products': updated_products
        }
        
        with open('product_database_pinecone.json', 'w') as f:
            json.dump(updated_database, f, indent=2)
        
        logger.info(f"Migration completed! {len(updated_products)} products migrated to Pinecone")
        return True
    else:
        logger.error("No products were successfully processed")
        return False

if __name__ == "__main__":
    asyncio.run(migrate_products_to_pinecone())
