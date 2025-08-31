#!/usr/bin/env python3

import pandas as pd
import json
import shutil
import os
from pathlib import Path
import random
from collections import defaultdict
import math

# Configuration
CSV_PATH = "/Users/kavya/Downloads/archive/Fashion Dataset.csv"
IMAGES_SOURCE = "/Users/kavya/Downloads/archive/Images/Images"
IMAGES_DEST = "backend/images"
TARGET_CATEGORIES = 50
PRODUCTS_PER_CATEGORY = 8  # Aim for 8 products per category
MAX_TOTAL_PRODUCTS = 400   # 50 categories * 8 products

def analyze_csv_categories():
    """Analyze the CSV to understand available categories and attributes"""
    print("Loading and analyzing fashion dataset...")
    
    # Read CSV
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} products from CSV")
    
    # Extract categories from p_attributes column
    categories = set()
    product_types = set()
    
    for idx, row in df.iterrows():
        if pd.isna(row['p_attributes']):
            continue
            
        try:
            # Parse the attributes string (it's like a dictionary string)
            attrs_str = row['p_attributes']
            if 'Top Type' in attrs_str:
                # Extract Top Type
                start = attrs_str.find("'Top Type': '") + len("'Top Type': '")
                end = attrs_str.find("'", start)
                if end > start:
                    top_type = attrs_str[start:end]
                    categories.add(top_type)
            
            if 'Bottom Type' in attrs_str:
                # Extract Bottom Type  
                start = attrs_str.find("'Bottom Type': '") + len("'Bottom Type': '")
                end = attrs_str.find("'", start)
                if end > start:
                    bottom_type = attrs_str[start:end]
                    categories.add(bottom_type)
                    
            # Also check for other clothing types in the name
            name = str(row['name']).lower()
            if 'shirt' in name and 'Shirts' not in categories:
                categories.add('Shirts')
            elif 'dress' in name and 'Dresses' not in categories:
                categories.add('Dresses')
            elif 'skirt' in name and 'Skirts' not in categories:
                categories.add('Skirts')
            elif 'jacket' in name and 'Jackets' not in categories:
                categories.add('Jackets')
            elif 'blazer' in name and 'Blazers' not in categories:
                categories.add('Blazers')
            elif 'coat' in name and 'Coats' not in categories:
                categories.add('Coats')
            elif 'sweater' in name and 'Sweaters' not in categories:
                categories.add('Sweaters')
            elif 'cardigan' in name and 'Cardigans' not in categories:
                categories.add('Cardigans')
            elif 'jumpsuit' in name and 'Jumpsuits' not in categories:
                categories.add('Jumpsuits')
                
        except Exception as e:
            continue
    
    categories = list(categories)[:TARGET_CATEGORIES]  # Limit to target number
    print(f"Found {len(categories)} unique categories:")
    for cat in sorted(categories):
        print(f"  - {cat}")
    
    return df, categories

def create_category_mapping(df, categories):
    """Create mapping of categories to product indices"""
    category_products = defaultdict(list)
    
    for idx, row in df.iterrows():
        if pd.isna(row['p_attributes']) or pd.isna(row['name']):
            continue
            
        attrs_str = str(row['p_attributes'])
        name = str(row['name']).lower()
        assigned_category = None
        
        # Try to assign to a category
        for category in categories:
            if category in ['Kurta', 'Kurtas'] and 'kurta' in name:
                assigned_category = 'Kurtas'
                break
            elif category in ['Tops', 'Top'] and ('top' in name or 'kurti' in name):
                assigned_category = 'Tops'
                break
            elif category == 'Shirts' and 'shirt' in name:
                assigned_category = 'Shirts'
                break
            elif category == 'Dresses' and 'dress' in name:
                assigned_category = 'Dresses'
                break
            elif category == 'Skirts' and 'skirt' in name:
                assigned_category = 'Skirts'
                break
            elif category == 'Jackets' and 'jacket' in name:
                assigned_category = 'Jackets'
                break
            elif category == 'Blazers' and 'blazer' in name:
                assigned_category = 'Blazers'
                break
            elif category == 'Trousers' and ('trouser' in name or 'pant' in name):
                assigned_category = 'Trousers'
                break
            elif category == 'Palazzos' and 'palazzo' in name:
                assigned_category = 'Palazzos'
                break
            elif f"'{category}'" in attrs_str:
                assigned_category = category
                break
        
        # If no category assigned, use a generic one based on name
        if not assigned_category:
            if 'kurta' in name:
                assigned_category = 'Kurtas'
            elif 'top' in name or 'kurti' in name:
                assigned_category = 'Tops'
            elif 'shirt' in name:
                assigned_category = 'Shirts'
            else:
                assigned_category = 'Fashion'  # Generic category
        
        if assigned_category:
            category_products[assigned_category].append(idx)
    
    return category_products

def select_diverse_products(df, category_products, max_products=MAX_TOTAL_PRODUCTS):
    """Select diverse products ensuring good category distribution"""
    selected_products = []
    
    # Calculate products per category
    active_categories = [cat for cat, products in category_products.items() if len(products) > 0]
    products_per_category = min(PRODUCTS_PER_CATEGORY, max_products // len(active_categories))
    
    print(f"Selecting {products_per_category} products from each of {len(active_categories)} categories")
    
    for category, product_indices in category_products.items():
        if not product_indices:
            continue
            
        # Randomly sample products from this category
        sample_size = min(products_per_category, len(product_indices))
        selected_indices = random.sample(product_indices, sample_size)
        
        for idx in selected_indices:
            row = df.iloc[idx]
            # Basic metadata only as requested
            product = {
                'product_id': str(int(row['p_id'])),
                'product_name': row['name'],
                'category': category,
                'image_path': f"images/{len(selected_products)}.jpg",  # Sequential naming
                'source_image_index': idx  # For copying the right image
            }
            selected_products.append(product)
    
    print(f"Selected {len(selected_products)} products total")
    return selected_products

def copy_images(selected_products):
    """Copy selected images to backend/images directory"""
    print("Copying images to backend/images...")
    
    # Create destination directory
    dest_dir = Path(IMAGES_DEST)
    dest_dir.mkdir(exist_ok=True)
    
    # Clear existing images (except README.md)
    for file in dest_dir.glob("*.jpg"):
        file.unlink()
    
    copied_count = 0
    
    for i, product in enumerate(selected_products):
        source_image = Path(IMAGES_SOURCE) / f"{product['source_image_index']}.jpg"
        dest_image = dest_dir / f"{i}.jpg"
        
        if source_image.exists():
            try:
                shutil.copy2(source_image, dest_image)
                # Update the product's image path to match the copied file
                product['image_path'] = f"images/{i}.jpg"
                copied_count += 1
            except Exception as e:
                print(f"Error copying {source_image}: {e}")
                # Use a placeholder path
                product['image_path'] = f"images/placeholder.jpg"
        else:
            print(f"Source image not found: {source_image}")
            product['image_path'] = f"images/placeholder.jpg"
    
    print(f"Successfully copied {copied_count} images")
    return copied_count

def generate_embeddings(selected_products):
    """Generate simple feature-based embeddings for products"""
    print("Generating embeddings...")
    
    for product in selected_products:
        # Create a simple embedding based on product features
        embedding = [0.0] * 50  # 50-dimensional embedding
        
        # Name-based features for similarity
        name = product['product_name'].lower()
        
        # Color features (first 10 dimensions)
        if 'black' in name:
            embedding[0] = 0.9
        elif 'white' in name:
            embedding[1] = 0.9
        elif 'red' in name:
            embedding[2] = 0.9
        elif 'blue' in name:
            embedding[3] = 0.9
        elif 'green' in name:
            embedding[4] = 0.9
        elif 'pink' in name:
            embedding[5] = 0.9
        elif 'yellow' in name:
            embedding[6] = 0.9
        elif 'purple' in name:
            embedding[7] = 0.9
        elif 'orange' in name:
            embedding[8] = 0.9
        elif 'brown' in name or 'beige' in name:
            embedding[9] = 0.9
        
        # Category features (dimensions 10-25)
        category = product['category'].lower()
        if 'kurta' in category:
            embedding[10] = 0.8
        elif 'top' in category:
            embedding[11] = 0.8
        elif 'shirt' in category:
            embedding[12] = 0.8
        elif 'dress' in category:
            embedding[13] = 0.8
        elif 'skirt' in category:
            embedding[14] = 0.8
        elif 'trouser' in category:
            embedding[15] = 0.8
        elif 'palazzo' in category:
            embedding[16] = 0.8
        
        # Pattern features (dimensions 25-35)
        if 'floral' in name:
            embedding[25] = 0.7
        elif 'stripe' in name:
            embedding[26] = 0.7
        elif 'solid' in name:
            embedding[27] = 0.7
        elif 'print' in name:
            embedding[28] = 0.7
        elif 'embroidered' in name:
            embedding[29] = 0.7
        
        # Random features for diversity (dimensions 35-50)
        for i in range(35, 50):
            embedding[i] = random.random() * 0.5
        
        product['embedding'] = embedding
    
    return selected_products

def create_database(selected_products):
    """Create the final database structure"""
    # Count categories
    category_counts = defaultdict(int)
    for product in selected_products:
        category_counts[product['category']] += 1
    
    database = {
        "metadata": {
            "total_products": len(selected_products),
            "embedding_model": "diverse_feature_based",
            "embedding_dimension": 50,
            "categories_used": list(category_counts.keys()),
            "category_counts": dict(category_counts),
            "generation_timestamp": pd.Timestamp.now().isoformat(),
            "generation_method": "diverse_csv_selection",
            "note": f"Diverse database with {len(category_counts)} categories from 14k fashion dataset"
        },
        "products": []
    }
    
    # Clean up products (remove source_image_index, keep only basic metadata)
    for product in selected_products:
        clean_product = {
            'product_id': product['product_id'],
            'product_name': product['product_name'],
            'category': product['category'],
            'image_path': product['image_path'],
            'embedding': product['embedding']
        }
        database["products"].append(clean_product)
    
    return database

def main():
    """Main function to create diverse database"""
    print("Creating diverse fashion product database...")
    
    # Step 1: Analyze CSV
    df, categories = analyze_csv_categories()
    
    # Step 2: Create category mapping
    category_products = create_category_mapping(df, categories)
    
    print("\nCategory distribution:")
    for cat, products in category_products.items():
        print(f"  {cat}: {len(products)} products available")
    
    # Step 3: Select diverse products
    random.seed(42)  # For reproducible results
    selected_products = select_diverse_products(df, category_products)
    
    # Step 4: Copy images
    copied_count = copy_images(selected_products)
    
    # Step 5: Generate embeddings
    selected_products = generate_embeddings(selected_products)
    
    # Step 6: Create database
    database = create_database(selected_products)
    
    # Save database
    output_path = "backend/product_database_deploy.json"
    with open(output_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"\n✅ Created diverse database with:")
    print(f"   • {len(selected_products)} products")
    print(f"   • {len(database['metadata']['categories_used'])} categories")
    print(f"   • {copied_count} images copied")
    print(f"   • Saved to {output_path}")
    
    print("\nCategories included:")
    for cat, count in database['metadata']['category_counts'].items():
        print(f"   • {cat}: {count} products")

if __name__ == "__main__":
    main()
