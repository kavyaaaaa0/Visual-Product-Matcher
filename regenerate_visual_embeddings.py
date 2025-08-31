#!/usr/bin/env python3

import json
import os
from pathlib import Path
from PIL import Image
import math

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

def extract_visual_features(image_path):
    """Extract comprehensive visual features from an image file"""
    try:
        image = Image.open(image_path)
        
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
            
            # Shape approximation
            # Count edge pixels (approximation)
            edge_pixel_count = sum(1 for e in edge_responses if e > 30) if edge_responses else 0
            edge_density = edge_pixel_count / len(rgb_pixels) if rgb_pixels else 0
            
            # Color uniformity
            color_ranges = []
            for channel in range(3):
                channel_vals = [p[channel] for p in rgb_pixels]
                color_ranges.append((max(channel_vals) - min(channel_vals)) / 255.0)
            avg_color_range = mean(color_ranges)
            
            features.extend([edge_density, avg_color_range])
        
        # Ensure exactly 50 dimensions
        while len(features) < 50:
            features.append(0.05)
        features = features[:50]
        
        return features
        
    except Exception as e:
        print(f"Error extracting features from {image_path}: {e}")
        return [0.1] * 50

def regenerate_database_embeddings():
    """Regenerate all product embeddings using actual visual features"""
    
    print("🔄 Regenerating database with visual embeddings...")
    
    # Load current database
    db_path = "backend/product_database_deploy.json"
    if not Path(db_path).exists():
        print("❌ Database file not found!")
        return False
    
    with open(db_path, 'r') as f:
        database = json.load(f)
    
    products = database.get('products', [])
    print(f"📊 Processing {len(products)} products...")
    
    # Regenerate embeddings for each product
    updated_count = 0
    for i, product in enumerate(products):
        image_path = Path("backend") / product['image_path']
        
        if image_path.exists():
            print(f"Processing {i+1}/{len(products)}: {product['category']} - {image_path.name}")
            
            # Extract visual features from the actual image
            visual_embedding = extract_visual_features(image_path)
            
            if visual_embedding:
                product['embedding'] = visual_embedding
                updated_count += 1
            else:
                print(f"⚠️  Failed to extract features for {image_path}")
        else:
            print(f"⚠️  Image not found: {image_path}")
    
    print(f"✅ Updated {updated_count} product embeddings")
    
    # Update metadata
    database['metadata']['embedding_model'] = "visual_feature_based"
    database['metadata']['note'] = f"Database with visual embeddings extracted from actual product images"
    database['metadata']['generation_timestamp'] = pd.Timestamp.now().isoformat()
    
    # Save updated database
    with open(db_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"💾 Saved updated database to {db_path}")
    
    # Also update the root copy
    root_db_path = "product_database_deploy.json"
    with open(root_db_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"💾 Updated root database copy: {root_db_path}")
    
    return True

if __name__ == "__main__":
    import pandas as pd
    regenerate_database_embeddings()
