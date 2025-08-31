#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from backend.similarity import extract_visual_features_from_image, calculate_enhanced_similarity
from PIL import Image

def test_similarity_system():
    """Test the improved similarity system to ensure proper garment type matching"""
    
    print("🧪 Testing Improved Visual Similarity System...")
    
    # Load database
    with open('product_database_deploy.json', 'r') as f:
        database = json.load(f)
    
    products = database['products']
    
    # Test cases: Select products from different categories
    test_cases = {
        'Trousers': [],
        'Dresses': [],
        'Tops': [],
        'Skirts': []
    }
    
    # Find test products
    for product in products:
        category = product['category']
        if category in test_cases and len(test_cases[category]) < 2:
            test_cases[category].append(product)
    
    print(f"📋 Found test products:")
    for category, items in test_cases.items():
        print(f"  {category}: {len(items)} products")
    
    # Test similarity within and across categories
    print("\n🔍 Testing Similarity Matching...")
    
    for test_category, test_products in test_cases.items():
        if len(test_products) < 1:
            continue
            
        test_product = test_products[0]
        test_embedding = test_product['embedding']
        
        print(f"\n--- Testing {test_category}: {test_product['product_name'][:50]}... ---")
        
        similarities = []
        for product in products:
            if product['product_id'] == test_product['product_id']:
                continue
                
            similarity = calculate_enhanced_similarity(test_embedding, product['embedding'])
            similarities.append({
                'category': product['category'],
                'name': product['product_name'][:30] + "...",
                'similarity': similarity
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Show top 10 matches
        print("Top 10 Similar Products:")
        same_category_count = 0
        for i, match in enumerate(similarities[:10]):
            marker = "✅" if match['category'] == test_category else "❌"
            if match['category'] == test_category:
                same_category_count += 1
            print(f"{i+1:2d}. {marker} {match['similarity']:.3f} | {match['category']} | {match['name']}")
        
        accuracy = (same_category_count / 10) * 100
        print(f"🎯 Same-category accuracy in top 10: {accuracy:.1f}% ({same_category_count}/10)")
        
        # Check if any wrong categories are ranking too high
        wrong_categories_in_top_3 = sum(1 for match in similarities[:3] if match['category'] != test_category)
        if wrong_categories_in_top_3 > 0:
            print(f"⚠️  {wrong_categories_in_top_3} wrong categories in top 3 matches!")
        else:
            print("✅ No wrong categories in top 3 matches")
    
    print("\n" + "="*60)
    print("🏁 SIMILARITY TESTING COMPLETED")

if __name__ == "__main__":
    test_similarity_system()
