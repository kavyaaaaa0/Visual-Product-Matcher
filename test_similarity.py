#!/usr/bin/env python3

import json
from pathlib import Path
from backend.similarity import generate_query_embedding, find_similar_products

def test_similarity_matching():
    """Test that visual similarity matching works correctly"""
    
    print("Testing visual similarity matching...")
    
    # Load database
    db_path = "backend/product_database_deploy.json"
    if not Path(db_path).exists():
        print("Database file not found!")
        return False
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    print(f"Loaded database with {len(database['products'])} products")
    
    # Test cases: try similarity search with actual product images
    test_cases = [
        {"image": "backend/images/69.jpg", "expected_category": "Shirts", "description": "Shirt image"},
        {"image": "backend/images/77.jpg", "expected_category": "Dresses", "description": "Dress image"},
        {"image": "backend/images/85.jpg", "expected_category": "Skirts", "description": "Skirt image"},
        {"image": "backend/images/48.jpg", "expected_category": "Jackets", "description": "Jacket image"},
        {"image": "backend/images/16.jpg", "expected_category": "Kurtas", "description": "Kurta image"}
    ]
    
    for i, test_case in enumerate(test_cases):
        image_path = Path(test_case["image"])
        if not image_path.exists():
            print(f"Test image not found: {image_path}")
            continue
            
        print(f"\nTest {i+1}: {test_case['description']} ({image_path.name})")
        print(f"   Expected category: {test_case['expected_category']}")
        
        # Generate embedding for test image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        query_embedding = generate_query_embedding(image_data)
        
        if not query_embedding:
            print("   Failed to generate embedding")
            continue
        
        # Find similar products
        similar_products = find_similar_products(
            query_embedding, 
            database, 
            min_similarity=0.0, 
            max_results=5
        )
        
        if not similar_products:
            print("   No similar products found")
            continue
        
        print(f"   Top 5 similar products:")
        category_matches = 0
        
        for j, product in enumerate(similar_products):
            similarity_percent = product['similarity_score'] * 100
            is_match = product['category'] == test_case['expected_category']
            match_indicator = "MATCH" if is_match else "DIFF"
            
            if is_match:
                category_matches += 1
            
            print(f"     {j+1}. [{match_indicator}] {product['category']} - {similarity_percent:.1f}% - {product['product_name'][:50]}...")
        
        accuracy = (category_matches / len(similar_products)) * 100
        print(f"   Category accuracy: {accuracy:.1f}% ({category_matches}/{len(similar_products)} matches)")
        
        if accuracy >= 60:
            print(f"   RESULT: GOOD - High category accuracy")
        elif accuracy >= 20:
            print(f"   RESULT: MODERATE - Some category matches")
        else:
            print(f"   RESULT: POOR - Low category accuracy")
    
    print(f"\nSimilarity testing complete!")
    return True

if __name__ == "__main__":
    test_similarity_matching()
