#!/usr/bin/env python3

import json
import os
from pathlib import Path

def fix_image_paths():
    """Fix image paths in the product database to match available images"""
    
    # Check available images
    images_dir = Path("backend/images")
    available_images = []
    
    if images_dir.exists():
        for img_file in images_dir.glob("*.jpg"):
            available_images.append(img_file.name)
    
    print(f"Found {len(available_images)} available images: {available_images}")
    
    # Load the database
    db_path = "backend/product_database_deploy.json"
    if not Path(db_path).exists():
        print(f"Database file {db_path} not found!")
        return False
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    print(f"Database has {len(database['products'])} products")
    
    # Create a mapping of image indices to available images
    image_mapping = {}
    for i, img_name in enumerate(available_images):
        # Extract the number from filename (e.g., "0.jpg" -> 0)
        img_num = img_name.replace('.jpg', '')
        if img_num.isdigit():
            image_mapping[int(img_num)] = f"images/{img_name}"
    
    print(f"Image mapping: {image_mapping}")
    
    # Filter products to only include those with available images
    valid_products = []
    
    for product in database['products']:
        # Extract image index from the current path
        # e.g., "dataset/Images/Images/0.jpg" -> 0
        current_path = product['image_path']
        filename = Path(current_path).name  # e.g., "0.jpg"
        img_num_str = filename.replace('.jpg', '')
        
        if img_num_str.isdigit():
            img_num = int(img_num_str)
            
            # If we have this image available, update the product
            if img_num in image_mapping:
                product['image_path'] = image_mapping[img_num]
                valid_products.append(product)
    
    print(f"Found {len(valid_products)} products with available images")
    
    # Update the database
    database['products'] = valid_products
    database['metadata']['total_products'] = len(valid_products)
    database['metadata']['note'] = "Sample database with available images only"
    
    # Save the updated database
    output_path = "backend/product_database_deploy.json"
    with open(output_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"Updated database saved to {output_path}")
    print(f"Database now contains {len(valid_products)} products with correct image paths")
    
    return True

if __name__ == "__main__":
    fix_image_paths()
