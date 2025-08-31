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

def extract_visual_features_from_image(image: Image.Image) -> List[float]:
    """Extract comprehensive visual features from a PIL Image - matches database generation"""
    try:
        # Resize for consistency
        if image.width > 224 or image.height > 224:
            image.thumbnail((224, 224), Image.Resampling.LANCZOS)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        features = []
        
        # Get pixel data
        rgb_pixels = list(image.getdata())
        
        if rgb_pixels:
            # 1. RGB statistics (6 features: mean + std for each channel)
            rgb_means = [mean([p[i] for p in rgb_pixels]) / 255.0 for i in range(3)]
            rgb_stds = [std_dev([p[i] for p in rgb_pixels]) / 255.0 for i in range(3)]
            features.extend(rgb_means + rgb_stds)
            
            # 2. Color histograms (15 features: 5 bins per RGB channel)
            for channel in range(3):
                rgb_vals = [p[channel] for p in rgb_pixels]
                hist = simple_histogram(rgb_vals, bins=5, range_min=0, range_max=255)
                hist_norm = [h / len(rgb_pixels) for h in hist]
                features.extend(hist_norm)
            
            # 3. Brightness and contrast (2 features)
            brightness_vals = [sum(p) / 3 for p in rgb_pixels]
            brightness = mean(brightness_vals) / 255.0
            contrast = std_dev(brightness_vals) / 255.0
            features.extend([brightness, contrast])
            
            # 4. Color dominance (10 features)
            # Dominant colors
            red_dominant = 1.0 if rgb_means[0] > max(rgb_means[1], rgb_means[2]) + 0.1 else 0.0
            green_dominant = 1.0 if rgb_means[1] > max(rgb_means[0], rgb_means[2]) + 0.1 else 0.0
            blue_dominant = 1.0 if rgb_means[2] > max(rgb_means[0], rgb_means[1]) + 0.1 else 0.0
            
            # Color temperature
            warm = (rgb_means[0] + rgb_means[1] * 0.5) / 1.5  # Red + some yellow
            cool = (rgb_means[2] + rgb_means[1] * 0.3) / 1.3   # Blue + some green
            
            # Saturation estimation
            saturation_vals = []
            for p in rgb_pixels:
                max_val = max(p)
                min_val = min(p)
                sat = (max_val - min_val) / max_val if max_val > 0 else 0
                saturation_vals.append(sat)
            
            avg_saturation = mean(saturation_vals)
            saturation_variance = std_dev(saturation_vals)
            
            # Aspect ratio
            aspect_ratio = image.width / image.height if image.height > 0 else 1.0
            
            # Color complexity (how many distinct colors)
            unique_colors = len(set(rgb_pixels))
            color_complexity = min(unique_colors / len(rgb_pixels), 1.0)
            
            features.extend([red_dominant, green_dominant, blue_dominant, warm, cool, 
                           avg_saturation, saturation_variance, aspect_ratio, color_complexity])
            
            # 5. Texture approximation (17 features)
            # Edge detection approximation using pixel differences
            width, height = image.size
            edge_responses = []
            
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    # Get surrounding pixels
                    center = rgb_pixels[y * width + x]
                    right = rgb_pixels[y * width + (x + 1)]
                    bottom = rgb_pixels[(y + 1) * width + x]
                    
                    # Calculate gradients
                    grad_x = sum(abs(center[i] - right[i]) for i in range(3)) / 3
                    grad_y = sum(abs(center[i] - bottom[i]) for i in range(3)) / 3
                    edge_responses.append(math.sqrt(grad_x**2 + grad_y**2))
            
            if edge_responses:
                edge_mean = mean(edge_responses) / 255.0
                edge_std = std_dev(edge_responses) / 255.0
                edge_max = max(edge_responses) / 255.0
                
                # Edge histogram
                edge_hist = simple_histogram(edge_responses, bins=5, range_min=0, range_max=255)
                edge_hist_norm = [h / len(edge_responses) for h in edge_hist]
                
                features.extend([edge_mean, edge_std, edge_max] + edge_hist_norm)
            else:
                features.extend([0.1] * 8)  # 3 + 5 edge features
            
            # Additional texture features
            # Local variance (block-based texture)
            block_size = 8
            local_variances = []
            for y in range(0, height - block_size, block_size):
                for x in range(0, width - block_size, block_size):
                    block_pixels = []
                    for by in range(y, min(y + block_size, height)):
                        for bx in range(x, min(x + block_size, width)):
                            pixel = rgb_pixels[by * width + bx]
                            block_pixels.append(sum(pixel) / 3)  # Grayscale
                    
                    if block_pixels:
                        local_variances.append(std_dev(block_pixels) ** 2)
            
            if local_variances:
                texture_variance = mean(local_variances) / (255.0 ** 2)
                texture_uniformity = std_dev(local_variances) / (255.0 ** 2)
                features.extend([texture_variance, texture_uniformity])
            else:
                features.extend([0.1, 0.1])
            
            # Directional features (approximate)
            horizontal_energy = 0
            vertical_energy = 0
            diagonal_energy = 0
            
            for y in range(height - 1):
                for x in range(width - 1):
                    current = rgb_pixels[y * width + x]
                    right = rgb_pixels[y * width + (x + 1)] if x + 1 < width else current
                    bottom = rgb_pixels[(y + 1) * width + x] if y + 1 < height else current
                    diagonal = rgb_pixels[(y + 1) * width + (x + 1)] if (y + 1 < height and x + 1 < width) else current
                    
                    # Calculate directional differences
                    h_diff = sum(abs(current[i] - right[i]) for i in range(3))
                    v_diff = sum(abs(current[i] - bottom[i]) for i in range(3))
                    d_diff = sum(abs(current[i] - diagonal[i]) for i in range(3))
                    
                    horizontal_energy += h_diff
                    vertical_energy += v_diff
                    diagonal_energy += d_diff
            
            total_energy = horizontal_energy + vertical_energy + diagonal_energy
            if total_energy > 0:
                h_norm = horizontal_energy / total_energy
                v_norm = vertical_energy / total_energy
                d_norm = diagonal_energy / total_energy
                features.extend([h_norm, v_norm, d_norm])
            else:
                features.extend([0.33, 0.33, 0.33])
            
            # Shape approximation and garment-specific features
            # Count edge pixels (approximation)
            edge_pixel_count = sum(1 for e in edge_responses if e > 30) if edge_responses else 0
            edge_density = edge_pixel_count / len(rgb_pixels) if rgb_pixels else 0
            
            # Garment silhouette analysis
            # Analyze vertical vs horizontal structure (key for dress vs top vs skirt)
            vertical_structure = v_norm if 'v_norm' in locals() else 0.33
            horizontal_structure = h_norm if 'h_norm' in locals() else 0.33
            
            # Garment length indicator (aspect ratio analysis)
            garment_length_indicator = aspect_ratio
            if aspect_ratio > 1.5:  # Very tall - likely full dress
                length_category = 0.9
            elif aspect_ratio > 1.0:  # Moderately tall - top/kurta
                length_category = 0.6
            else:  # Wide - likely cropped/skirt
                length_category = 0.3
            
            # Edge concentration (where are most edges - important for garment boundaries)
            top_quarter_edges = 0
            bottom_quarter_edges = 0
            middle_edges = 0
            
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if y < height // 4:  # Top quarter
                        top_quarter_edges += 1 if edge_responses[y * (width-2) + x - y] > 30 else 0
                    elif y > 3 * height // 4:  # Bottom quarter
                        bottom_quarter_edges += 1 if edge_responses[y * (width-2) + x - y] > 30 else 0
                    else:  # Middle
                        middle_edges += 1 if edge_responses[y * (width-2) + x - y] > 30 else 0
            
            total_edge_pixels = max(top_quarter_edges + bottom_quarter_edges + middle_edges, 1)
            top_edge_ratio = top_quarter_edges / total_edge_pixels
            bottom_edge_ratio = bottom_quarter_edges / total_edge_pixels
            
            # Color uniformity (keep but reduce importance)
            color_ranges = []
            for channel in range(3):
                channel_vals = [p[channel] for p in rgb_pixels]
                color_ranges.append((max(channel_vals) - min(channel_vals)) / 255.0)
            avg_color_range = mean(color_ranges)
            
            features.extend([edge_density, length_category, vertical_structure, 
                           horizontal_structure, top_edge_ratio, bottom_edge_ratio, avg_color_range])
        
        # Ensure exactly 50 dimensions
        while len(features) < 50:
            features.append(0.05)
        features = features[:50]
        
        return features
        
    except Exception as e:
        print(f"Error extracting visual features: {e}")
        return [0.1] * 50

def generate_query_embedding(image_data: bytes) -> List[float]:
    """Generate visual embedding from uploaded image data"""
    try:
        image = Image.open(io.BytesIO(image_data))
        return extract_visual_features_from_image(image)
        
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        # Return default embedding with 50 dimensions
        return [0.1] * 50

def calculate_enhanced_similarity(query_embedding: List[float], product_embedding: List[float]) -> float:
    """Calculate similarity prioritizing garment shape/structure over color"""
    try:
        if len(query_embedding) != len(product_embedding) or len(query_embedding) != 50:
            return 0.0
        
        # Define feature importance weights - HEAVILY prioritize shape over color
        weights = [1.0] * 50
        
        # Color features (dims 0-22) - MINIMAL importance for garment type matching
        for i in range(6):  # RGB means and stds
            weights[i] = 0.05  # Nearly ignore color
        for i in range(6, 21):  # Color histograms
            weights[i] = 0.1   # Nearly ignore color distribution
        for i in range(21, 23):  # Brightness and contrast
            weights[i] = 0.2
        
        # Color dominance and temperature (dims 23-32) - MINIMAL importance
        for i in range(23, 33):
            weights[i] = 0.1   # Nearly ignore color temperature
        
        # Texture and edge features (dims 33-49) - MAXIMUM importance for garment type
        for i in range(33, 41):  # Edge detection features
            weights[i] = 5.0   # Maximum weight for shape detection
        for i in range(41, 43):  # Texture variance features
            weights[i] = 4.0
        for i in range(43, 46):  # Directional features (crucial for garment shape)
            weights[i] = 6.0   # Absolute highest weight for garment structure
        for i in range(46, 50):  # Shape-specific features we added
            weights[i] = 5.5   # Very high weight for garment silhouette
        
        # Aspect ratio and shape features - MAXIMUM importance
        if len(weights) > 31:  # Aspect ratio position
            weights[31] = 8.0  # Extremely critical for garment type (dress vs skirt vs top)
        
        # Calculate weighted cosine similarity
        weighted_dot_product = sum(w * a * b for w, a, b in zip(weights, query_embedding, product_embedding))
        
        # Calculate weighted magnitudes
        weighted_magnitude1 = math.sqrt(sum(w * a * a for w, a in zip(weights, query_embedding)))
        weighted_magnitude2 = math.sqrt(sum(w * b * b for w, b in zip(weights, product_embedding)))
        
        # Avoid division by zero
        if weighted_magnitude1 == 0 or weighted_magnitude2 == 0:
            return 0.0
            
        # Calculate weighted cosine similarity
        similarity = weighted_dot_product / (weighted_magnitude1 * weighted_magnitude2)
        return float(similarity)
        
    except Exception as e:
        print(f"Error calculating enhanced similarity: {e}")
        return 0.0

def find_similar_products(
    query_embedding: List[float], 
    product_database: Dict, 
    min_similarity: float = 0.0,
    max_results: int = 10
) -> List[Dict]:
    """Find similar products using enhanced visual similarity"""
    
    if not query_embedding:
        return []
    
    products = product_database.get('products', [])
    similarities = []
    
    # Calculate similarities
    for product in products:
        if 'embedding' in product and product['embedding']:
            # Use enhanced similarity calculation
            similarity = calculate_enhanced_similarity(query_embedding, product['embedding'])
            
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
