#!/usr/bin/env python3

import json
import os
from pathlib import Path

def test_database_and_images():
    """Test that database and images are properly set up"""
    
    print("🔍 Testing Visual Product Matcher setup...")
    
    # Test 1: Database exists and loads
    db_path = "backend/product_database_deploy.json"
    if not Path(db_path).exists():
        print("❌ Database file not found!")
        return False
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    products = database.get('products', [])
    categories = database.get('metadata', {}).get('categories_used', [])
    
    print(f"✅ Database loaded: {len(products)} products, {len(categories)} categories")
    
    # Test 2: Check image files exist
    images_dir = Path("backend/images")
    if not images_dir.exists():
        print("❌ Images directory not found!")
        return False
    
    image_files = list(images_dir.glob("*.jpg"))
    print(f"✅ Found {len(image_files)} image files")
    
    # Test 3: Verify image paths match actual files
    missing_images = 0
    for product in products:
        image_path = product['image_path']
        # Convert "images/0.jpg" to "backend/images/0.jpg"
        full_path = Path("backend") / image_path
        if not full_path.exists():
            missing_images += 1
    
    if missing_images > 0:
        print(f"⚠️  {missing_images} products have missing image files")
    else:
        print("✅ All product images exist")
    
    # Test 4: Show category distribution
    print(f"\n📊 Category distribution:")
    category_counts = database.get('metadata', {}).get('category_counts', {})
    for category, count in sorted(category_counts.items()):
        print(f"   • {category}: {count} products")
    
    # Test 5: Show sample products
    print(f"\n🎯 Sample products:")
    for i, product in enumerate(products[:5]):
        print(f"   • {product['category']}: {product['product_name'][:50]}...")
    
    print(f"\n✅ Setup complete! Your Visual Product Matcher has:")
    print(f"   • {len(products)} diverse fashion products")
    print(f"   • {len(categories)} different categories")
    print(f"   • {len(image_files)} product images")
    print(f"   • Ready for deployment!")
    
    return True

if __name__ == "__main__":
    test_database_and_images()
