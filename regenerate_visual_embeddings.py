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

def detect_garment_silhouette(image):
    """Advanced garment silhouette detection for shape-based classification"""
    width, height = image.size
    rgb_pixels = list(image.getdata())
    
    # Convert to grayscale for shape analysis
    gray_pixels = [sum(p) / 3 for p in rgb_pixels]
    
    # 1. Garment boundary detection using edge concentration
    edges_per_row = []
    edges_per_col = []
    
    # Row-wise edge detection (horizontal boundaries)
    for y in range(height):
        row_edges = 0
        for x in range(width - 1):
            current = gray_pixels[y * width + x]
            next_pixel = gray_pixels[y * width + (x + 1)]
            if abs(current - next_pixel) > 30:  # Strong edge
                row_edges += 1
        edges_per_row.append(row_edges)
    
    # Column-wise edge detection (vertical boundaries)
    for x in range(width):
        col_edges = 0
        for y in range(height - 1):
            current = gray_pixels[y * width + x]
            next_pixel = gray_pixels[(y + 1) * width + x]
            if abs(current - next_pixel) > 30:  # Strong edge
                col_edges += 1
        edges_per_col.append(col_edges)
    
    # 2. Garment shape analysis
    aspect_ratio = width / height if height > 0 else 1.0
    
    # Classify garment structure based on aspect ratio and edge distribution
    if aspect_ratio > 1.8:  # Very wide - likely individual pants/trousers
        garment_type_score = 0.9  # High confidence for trousers/pants
        vertical_dominance = 0.8
    elif aspect_ratio > 1.3:  # Moderately wide - tops, shirts
        garment_type_score = 0.7
        vertical_dominance = 0.6
    elif 0.7 <= aspect_ratio <= 1.3:  # Square-ish - dresses, kurtas
        garment_type_score = 0.5
        vertical_dominance = 0.4
    elif aspect_ratio < 0.6:  # Very tall - full length dresses, sarees
        garment_type_score = 0.2
        vertical_dominance = 0.2
    else:
        garment_type_score = 0.5
        vertical_dominance = 0.5
    
    # 3. Structural pattern analysis
    # Analyze where the garment boundaries are most prominent
    top_third_edges = sum(edges_per_row[:height//3])
    middle_third_edges = sum(edges_per_row[height//3:2*height//3])
    bottom_third_edges = sum(edges_per_row[2*height//3:])
    
    total_horizontal_edges = top_third_edges + middle_third_edges + bottom_third_edges
    if total_horizontal_edges > 0:
        top_structure = top_third_edges / total_horizontal_edges
        middle_structure = middle_third_edges / total_horizontal_edges
        bottom_structure = bottom_third_edges / total_horizontal_edges
    else:
        top_structure = middle_structure = bottom_structure = 0.33
    
    # 4. Garment-specific shape indicators
    # Waistline detection (for separating tops from dresses)
    waist_region_start = int(height * 0.4)
    waist_region_end = int(height * 0.6)
    waist_edges = sum(edges_per_row[waist_region_start:waist_region_end])
    waist_prominence = waist_edges / max(total_horizontal_edges, 1)
    
    # Leg separation detection (for pants/trousers)
    bottom_quarter_start = int(height * 0.75)
    bottom_quarter_cols = edges_per_col[width//4:3*width//4]  # Middle columns
    leg_separation = max(bottom_quarter_cols) / max(sum(bottom_quarter_cols), 1) if bottom_quarter_cols else 0
    
    # Sleeve detection (prominent vertical edges in upper sides)
    sleeve_region_cols = edges_per_col[:width//4] + edges_per_col[3*width//4:]
    sleeve_prominence = sum(sleeve_region_cols) / max(sum(edges_per_col), 1)
    
    return {
        'aspect_ratio': aspect_ratio,
        'garment_type_score': garment_type_score,
        'vertical_dominance': vertical_dominance,
        'top_structure': top_structure,
        'middle_structure': middle_structure,
        'bottom_structure': bottom_structure,
        'waist_prominence': waist_prominence,
        'leg_separation': leg_separation,
        'sleeve_prominence': sleeve_prominence
    }

def extract_visual_features(image_path):
    """Extract advanced garment-focused visual features for accurate clothing classification"""
    try:
        image = Image.open(image_path)
        
        # Resize for consistency
        if image.width > 224 or image.height > 224:
            image.thumbnail((224, 224), Image.Resampling.LANCZOS)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        features = []
        width, height = image.size
        
        # Get pixel data
        rgb_pixels = list(image.getdata())
        
        if not rgb_pixels:
            return [0.1] * 50
        
        # === SECTION 1: GARMENT SHAPE ANALYSIS (17 features) ===
        # This is the most important section for distinguishing garment types
        
        silhouette_data = detect_garment_silhouette(image)
        
        # Core shape features (9 features)
        features.extend([
            silhouette_data['aspect_ratio'],
            silhouette_data['garment_type_score'],
            silhouette_data['vertical_dominance'],
            silhouette_data['top_structure'],
            silhouette_data['middle_structure'],
            silhouette_data['bottom_structure'],
            silhouette_data['waist_prominence'],
            silhouette_data['leg_separation'],
            silhouette_data['sleeve_prominence']
        ])
        
        # Advanced shape analysis (8 features)
        # Garment width distribution analysis
        row_widths = []
        for y in range(height):
            row_start = None
            row_end = None
            for x in range(width):
                pixel_intensity = sum(rgb_pixels[y * width + x]) / 3
                if pixel_intensity > 50:  # Non-background pixel
                    if row_start is None:
                        row_start = x
                    row_end = x
            
            if row_start is not None and row_end is not None:
                row_widths.append(row_end - row_start)
            else:
                row_widths.append(0)
        
        # Analyze garment width patterns
        if row_widths:
            top_quarter_width = mean(row_widths[:height//4]) if height//4 > 0 else 0
            middle_half_width = mean(row_widths[height//4:3*height//4]) if height//4 > 0 else 0
            bottom_quarter_width = mean(row_widths[3*height//4:]) if height//4 > 0 else 0
            
            max_width = max(row_widths) if row_widths else 1
            if max_width > 0:
                top_width_ratio = top_quarter_width / max_width
                middle_width_ratio = middle_half_width / max_width
                bottom_width_ratio = bottom_quarter_width / max_width
            else:
                top_width_ratio = middle_width_ratio = bottom_width_ratio = 0.5
            
            # Garment taper analysis (important for distinguishing fits)
            width_variance = std_dev(row_widths) / max_width if max_width > 0 else 0
            
            # A-line vs straight vs tapered analysis
            if bottom_width_ratio > top_width_ratio + 0.2:
                garment_fit = 0.8  # A-line (dresses, skirts)
            elif abs(bottom_width_ratio - top_width_ratio) < 0.1:
                garment_fit = 0.5  # Straight fit (trousers, shirts)
            else:
                garment_fit = 0.2  # Tapered (fitted tops)
        else:
            top_width_ratio = middle_width_ratio = bottom_width_ratio = 0.5
            width_variance = 0.1
            garment_fit = 0.5
        
        # Length-to-width ratio categories
        if silhouette_data['aspect_ratio'] < 0.6:  # Very long
            length_category = 0.9  # Full dress/saree
        elif silhouette_data['aspect_ratio'] < 1.0:  # Long
            length_category = 0.7  # Kurta/tunic
        elif silhouette_data['aspect_ratio'] < 1.5:  # Medium
            length_category = 0.5  # Top/shirt
        else:  # Wide
            length_category = 0.2  # Trousers/pants
        
        # Symmetry analysis (important for garment type)
        left_half_pixels = []
        right_half_pixels = []
        for y in range(height):
            for x in range(width//2):
                left_half_pixels.append(sum(rgb_pixels[y * width + x]) / 3)
            for x in range(width//2, width):
                right_half_pixels.append(sum(rgb_pixels[y * width + x]) / 3)
        
        left_mean = mean(left_half_pixels) if left_half_pixels else 0
        right_mean = mean(right_half_pixels) if right_half_pixels else 0
        symmetry_score = 1.0 - abs(left_mean - right_mean) / 255.0
        
        features.extend([
            top_width_ratio, middle_width_ratio, bottom_width_ratio,
            width_variance, garment_fit, length_category, symmetry_score
        ])
        
        # === SECTION 2: STRUCTURAL PATTERN ANALYSIS (15 features) ===
        
        # Advanced edge analysis for garment boundaries
        edge_responses = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                center = rgb_pixels[y * width + x]
                # Use Sobel-like operators for better edge detection
                neighbors = [
                    rgb_pixels[(y-1) * width + (x-1)],  # Top-left
                    rgb_pixels[(y-1) * width + x],       # Top
                    rgb_pixels[(y-1) * width + (x+1)],   # Top-right
                    rgb_pixels[y * width + (x-1)],       # Left
                    rgb_pixels[y * width + (x+1)],       # Right
                    rgb_pixels[(y+1) * width + (x-1)],   # Bottom-left
                    rgb_pixels[(y+1) * width + x],       # Bottom
                    rgb_pixels[(y+1) * width + (x+1)]    # Bottom-right
                ]
                
                # Calculate gradient magnitude
                gx = sum(abs(center[i] - neighbors[4][i]) for i in range(3))  # Horizontal gradient
                gy = sum(abs(center[i] - neighbors[6][i]) for i in range(3))  # Vertical gradient
                edge_strength = math.sqrt(gx**2 + gy**2)
                edge_responses.append(edge_strength)
        
        if edge_responses:
            edge_mean = mean(edge_responses) / 255.0
            edge_std = std_dev(edge_responses) / 255.0
            
            # Edge distribution analysis
            strong_edges = [e for e in edge_responses if e > 50]
            edge_density = len(strong_edges) / len(edge_responses)
            
            # Directional edge analysis
            horizontal_edges = 0
            vertical_edges = 0
            
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    idx = (y - 1) * (width - 2) + (x - 1)
                    if idx < len(edge_responses) and edge_responses[idx] > 30:
                        # Check if edge is more horizontal or vertical
                        center = rgb_pixels[y * width + x]
                        left = rgb_pixels[y * width + (x-1)]
                        right = rgb_pixels[y * width + (x+1)]
                        top = rgb_pixels[(y-1) * width + x]
                        bottom = rgb_pixels[(y+1) * width + x]
                        
                        h_diff = sum(abs(center[i] - left[i]) + abs(center[i] - right[i]) for i in range(3))
                        v_diff = sum(abs(center[i] - top[i]) + abs(center[i] - bottom[i]) for i in range(3))
                        
                        if h_diff > v_diff:
                            horizontal_edges += 1
                        else:
                            vertical_edges += 1
            
            total_directed_edges = horizontal_edges + vertical_edges
            h_edge_ratio = horizontal_edges / max(total_directed_edges, 1)
            v_edge_ratio = vertical_edges / max(total_directed_edges, 1)
            
            features.extend([edge_mean, edge_std, edge_density, h_edge_ratio, v_edge_ratio])
        else:
            features.extend([0.1, 0.1, 0.1, 0.5, 0.5])
        
        # Garment region analysis (10 features)
        # Divide image into regions and analyze content
        regions = {
            'top_left': (0, 0, width//2, height//3),
            'top_right': (width//2, 0, width, height//3),
            'middle_left': (0, height//3, width//2, 2*height//3),
            'middle_right': (width//2, height//3, width, 2*height//3),
            'bottom_left': (0, 2*height//3, width//2, height),
            'bottom_right': (width//2, 2*height//3, width, height)
        }
        
        region_features = []
        for region_name, (x1, y1, x2, y2) in regions.items():
            region_pixels = []
            for y in range(y1, y2):
                for x in range(x1, x2):
                    if y < height and x < width:
                        region_pixels.append(sum(rgb_pixels[y * width + x]) / 3)
            
            if region_pixels:
                region_intensity = mean(region_pixels) / 255.0
            else:
                region_intensity = 0.5
            
            region_features.extend([region_intensity])
        
        # Add overall structural features
        center_mass_x = 0
        center_mass_y = 0
        total_mass = 0
        
        for y in range(height):
            for x in range(width):
                pixel_intensity = sum(rgb_pixels[y * width + x]) / 3
                if pixel_intensity > 50:  # Non-background
                    center_mass_x += x * pixel_intensity
                    center_mass_y += y * pixel_intensity
                    total_mass += pixel_intensity
        
        if total_mass > 0:
            center_x = (center_mass_x / total_mass) / width
            center_y = (center_mass_y / total_mass) / height
        else:
            center_x = center_y = 0.5
        
        # Symmetry in structure
        structural_symmetry = 1.0 - abs(center_x - 0.5) * 2
        
        # Length distribution (key for distinguishing garment types)
        garment_coverage = total_mass / (width * height * 255.0)
        
        features.extend(region_features + [center_x, center_y, structural_symmetry, garment_coverage])
        
        # === SECTION 3: MINIMAL COLOR FEATURES (10 features) ===
        # Reduced color importance for better shape-based matching
        
        # Basic color statistics (6 features)
        rgb_means = [mean([p[i] for p in rgb_pixels]) / 255.0 for i in range(3)]
        rgb_stds = [std_dev([p[i] for p in rgb_pixels]) / 255.0 for i in range(3)]
        features.extend(rgb_means + rgb_stds)
        
        # Color uniformity (4 features)
        color_ranges = []
        for channel in range(3):
            channel_vals = [p[channel] for p in rgb_pixels]
            color_ranges.append((max(channel_vals) - min(channel_vals)) / 255.0)
        avg_color_range = mean(color_ranges)
        
        # Brightness analysis
        brightness_vals = [sum(p) / 3 for p in rgb_pixels]
        brightness = mean(brightness_vals) / 255.0
        contrast = std_dev(brightness_vals) / 255.0
        
        # Dominant color detection (simplified)
        dominant_channel = rgb_means.index(max(rgb_means))
        
        features.extend([avg_color_range, brightness, contrast, dominant_channel / 2.0])
        
        # === SECTION 4: TEXTURE ANALYSIS (5 features) ===
        # Keep minimal texture analysis
        
        # Local texture variance
        block_size = 16
        local_variances = []
        for y in range(0, height - block_size, block_size):
            for x in range(0, width - block_size, block_size):
                block_pixels = []
                for by in range(y, min(y + block_size, height)):
                    for bx in range(x, min(x + block_size, width)):
                        pixel = rgb_pixels[by * width + bx]
                        block_pixels.append(sum(pixel) / 3)
                
                if block_pixels:
                    local_variances.append(std_dev(block_pixels))
        
        if local_variances:
            texture_mean = mean(local_variances) / 255.0
            texture_std = std_dev(local_variances) / 255.0
            texture_uniformity = 1.0 - (texture_std / max(texture_mean, 0.001))
        else:
            texture_mean = texture_std = 0.1
            texture_uniformity = 0.5
        
        # Pattern regularity
        pattern_score = min(texture_uniformity, 1.0)
        complexity_score = min(len(set(rgb_pixels)) / len(rgb_pixels), 1.0)
        
        features.extend([texture_mean, texture_std, texture_uniformity, pattern_score, complexity_score])
        
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
