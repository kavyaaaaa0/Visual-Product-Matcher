import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import io

def calculate_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    try:
        vec1 = np.array(embedding1).reshape(1, -1)
        vec2 = np.array(embedding2).reshape(1, -1)
        similarity = cosine_similarity(vec1, vec2)[0][0]
        return float(similarity)
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0

def generate_query_embedding(image_data: bytes) -> List[float]:
    try:
        image = Image.open(io.BytesIO(image_data))
        
        if image.width > 224 or image.height > 224:
            image.thumbnail((224, 224), Image.Resampling.LANCZOS)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        features = []
        
        # Advanced color features
        pixels = list(image.getdata())
        if pixels:
            # RGB averages
            avg_r = sum(p[0] for p in pixels) / len(pixels) / 255.0
            avg_g = sum(p[1] for p in pixels) / len(pixels) / 255.0
            avg_b = sum(p[2] for p in pixels) / len(pixels) / 255.0
            
            # Color variance (important for texture)
            r_values = [p[0]/255.0 for p in pixels]
            g_values = [p[1]/255.0 for p in pixels]
            b_values = [p[2]/255.0 for p in pixels]
            
            r_var = np.var(r_values)
            g_var = np.var(g_values)
            b_var = np.var(b_values)
            
            # Aspect ratio
            aspect_ratio = image.width / image.height if image.height > 0 else 1.0
            
            features.extend([avg_r, avg_g, avg_b, r_var, g_var, b_var, aspect_ratio])
        else:
            features.extend([0.5, 0.5, 0.5, 0.1, 0.1, 0.1, 1.0])
        
        # Additional features to match database format (50 dimensions)
        # Brightness and contrast
        if pixels:
            brightness = sum(sum(p) for p in pixels) / (len(pixels) * 3) / 255.0
            features.append(brightness)
            
            # Color distribution (histogram-like features)
            for channel in range(3):  # RGB
                channel_values = [p[channel]/255.0 for p in pixels]
                # Simple histogram bins
                low_bin = sum(1 for v in channel_values if v < 0.33) / len(channel_values)
                mid_bin = sum(1 for v in channel_values if 0.33 <= v < 0.67) / len(channel_values)
                high_bin = sum(1 for v in channel_values if v >= 0.67) / len(channel_values)
                features.extend([low_bin, mid_bin, high_bin])
        else:
            features.extend([0.5, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33, 0.33])
        
        # Dominant color detection (simplified)
        if pixels:
            # Find dominant RGB ranges
            red_dominant = 1.0 if avg_r > max(avg_g, avg_b) + 0.1 else 0.0
            green_dominant = 1.0 if avg_g > max(avg_r, avg_b) + 0.1 else 0.0
            blue_dominant = 1.0 if avg_b > max(avg_r, avg_g) + 0.1 else 0.0
            
            features.extend([red_dominant, green_dominant, blue_dominant])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        # Pad to exactly 50 dimensions with deterministic values
        import hashlib
        hash_input = f"{sum(features):.6f}".encode()
        hash_obj = hashlib.md5(hash_input)
        random_seed = int(hash_obj.hexdigest()[:8], 16)
        np.random.seed(random_seed)
        
        while len(features) < 50:
            features.append(np.random.random() * 0.1)
        
        features = features[:50]  # Ensure exactly 50 dimensions
        
        return features
        
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        # Return default embedding with 50 dimensions
        return [0.1] * 50

def find_similar_products(
    query_embedding: List[float], 
    product_database: Dict, 
    min_similarity: float = 0.0,
    max_results: int = 10
) -> List[Dict]:
    """Find similar products using cosine similarity"""
    
    if not query_embedding:
        return []
    
    products = product_database.get('products', [])
    similarities = []
    
    # Calculate similarities
    for product in products:
        if 'embedding' in product and product['embedding']:
            similarity = calculate_cosine_similarity(query_embedding, product['embedding'])
            
            if similarity >= min_similarity:
                result = {
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'category': product['category'],
                    'image_path': product['image_path'],
                    'similarity_score': similarity
                }
                similarities.append(result)
    
    # Sort by similarity (descending) and return top results
    similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
    return similarities[:max_results]

def get_category_stats(product_database: Dict) -> Dict[str, int]:
    """Get statistics about categories in the database"""
    products = product_database.get('products', [])
    category_counts = {}
    
    for product in products:
        category = product.get('category', 'Uncategorized')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return category_counts
