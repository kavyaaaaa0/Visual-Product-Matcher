import math
from typing import List, Dict
from PIL import Image
import io

# TensorFlow is disabled for deployment simplicity
TF_HUB_AVAILABLE = False

def calculate_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    try:
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        return float(similarity)
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0

# Global model cache
_model_cache = None

def get_vision_model():
    """Get or load the vision model for feature extraction"""
    global _model_cache
    if _model_cache is None and TF_HUB_AVAILABLE:
        try:
            # Use MobileNet for lightweight feature extraction
            _model_cache = hub.load("https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/5")
            print("Loaded MobileNet model for enhanced similarity")
        except Exception as e:
            print(f"Failed to load TF Hub model: {e}")
            _model_cache = False
    return _model_cache if _model_cache is not False else None

def generate_deep_features(image: Image.Image) -> List[float]:
    """Extract deep learning features from image"""
    model = get_vision_model()
    if model is None:
        return []
    
    try:
        # Prepare image for model
        img_array = np.array(image.resize((224, 224)))
        img_array = img_array / 255.0  # Normalize
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
        # Extract features
        features = model(img_array)
        return features.numpy().flatten()[:128].tolist()  # Use first 128 features
    except Exception as e:
        print(f"Error extracting deep features: {e}")
        return []

def mean(values):
    return sum(values) / len(values) if values else 0

def std_dev(values):
    if not values:
        return 0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def simple_histogram(values, bins=5, range_min=0, range_max=255):
    """Simple histogram implementation"""
    bin_width = (range_max - range_min) / bins
    hist = [0] * bins
    
    for val in values:
        bin_index = min(int((val - range_min) / bin_width), bins - 1)
        if bin_index >= 0:
            hist[bin_index] += 1
    
    return hist

def generate_enhanced_color_features(image: Image.Image) -> List[float]:
    """Generate enhanced color and texture features"""
    features = []
    
    # Convert to different color spaces for better analysis
    rgb_img = image.convert('RGB')
    
    # RGB analysis
    rgb_pixels = list(rgb_img.getdata())
    
    if rgb_pixels:
        # RGB statistics
        rgb_means = [mean([p[i] for p in rgb_pixels]) / 255.0 for i in range(3)]
        rgb_stds = [std_dev([p[i] for p in rgb_pixels]) / 255.0 for i in range(3)]
        
        features.extend(rgb_means + rgb_stds)
        
        # Color distribution (histogram)
        for channel in range(3):
            rgb_vals = [p[channel] for p in rgb_pixels]
            hist = simple_histogram(rgb_vals, bins=5, range_min=0, range_max=255)
            hist_norm = [h / len(rgb_pixels) for h in hist]
            features.extend(hist_norm)
        
        # Brightness and contrast  
        brightness_vals = [sum(p) / 3 for p in rgb_pixels]
        brightness = mean(brightness_vals) / 255.0
        contrast = std_dev(brightness_vals) / 255.0
        features.extend([brightness, contrast])
    
    return features

def generate_query_embedding(image_data: bytes) -> List[float]:
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Resize for consistency
        if image.width > 224 or image.height > 224:
            image.thumbnail((224, 224), Image.Resampling.LANCZOS)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Try to use enhanced features first
        enhanced_features = generate_enhanced_color_features(image)
        if enhanced_features and len(enhanced_features) >= 30:
            # Use enhanced features, pad to 50
            features = enhanced_features[:30]
            
            # Add some deep features if available
            deep_features = generate_deep_features(image)
            if deep_features:
                features.extend(deep_features[:20])  # Add 20 deep features
            else:
                # Fallback features
                features.extend([0.1] * 20)
                
        else:
            # Fallback to original method
            features = []
            pixels = list(image.getdata())
            
            if pixels:
                # RGB averages
                avg_r = sum(p[0] for p in pixels) / len(pixels) / 255.0
                avg_g = sum(p[1] for p in pixels) / len(pixels) / 255.0
                avg_b = sum(p[2] for p in pixels) / len(pixels) / 255.0
                
                # Color variance
                r_values = [p[0]/255.0 for p in pixels]
                g_values = [p[1]/255.0 for p in pixels]
                b_values = [p[2]/255.0 for p in pixels]
                
                r_var = std_dev(r_values) ** 2  # variance is std dev squared
                g_var = std_dev(g_values) ** 2
                b_var = std_dev(b_values) ** 2
                
                aspect_ratio = image.width / image.height if image.height > 0 else 1.0
                features.extend([avg_r, avg_g, avg_b, r_var, g_var, b_var, aspect_ratio])
                
                # Brightness
                brightness = sum(sum(p) for p in pixels) / (len(pixels) * 3) / 255.0
                features.append(brightness)
                
                # Color distribution
                for channel in range(3):
                    channel_values = [p[channel]/255.0 for p in pixels]
                    low_bin = sum(1 for v in channel_values if v < 0.33) / len(channel_values)
                    mid_bin = sum(1 for v in channel_values if 0.33 <= v < 0.67) / len(channel_values)
                    high_bin = sum(1 for v in channel_values if v >= 0.67) / len(channel_values)
                    features.extend([low_bin, mid_bin, high_bin])
                
                # Dominant colors
                red_dominant = 1.0 if avg_r > max(avg_g, avg_b) + 0.1 else 0.0
                green_dominant = 1.0 if avg_g > max(avg_r, avg_b) + 0.1 else 0.0
                blue_dominant = 1.0 if avg_b > max(avg_r, avg_g) + 0.1 else 0.0
                features.extend([red_dominant, green_dominant, blue_dominant])
            else:
                features = [0.5, 0.5, 0.5, 0.1, 0.1, 0.1, 1.0, 0.5] + [0.33] * 9 + [0.0] * 3
        
        # Ensure exactly 50 dimensions
        while len(features) < 50:
            features.append(0.05)
        features = features[:50]
        
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
