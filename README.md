# Visual Product Matcher

AI-powered visual similarity search for fashion products using computer vision

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://visual-product-matcher-xi.vercel.app)
[![Backend API](https://img.shields.io/badge/API-Docs-blue)](https://visual-product-matcher-p5u4.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Live Deployments

- **Frontend Application**: [https://visual-product-matcher-xi.vercel.app](https://visual-product-matcher-xi.vercel.app)
- **Backend API**: [https://visual-product-matcher-p5u4.onrender.com](https://visual-product-matcher-p5u4.onrender.com)
- **API Documentation**: [https://visual-product-matcher-p5u4.onrender.com/docs](https://visual-product-matcher-p5u4.onrender.com/docs)

## Important Note

**This application is specifically designed for fashion products only.** It works with clothing items such as dresses, tops, trousers, skirts, shirts, jackets, and other fashion garments. The visual similarity algorithms are optimized for fashion product categories and may not work effectively with other types of products.

## Features

### Core Functionality
- Visual search by uploading images or providing URLs
- Garment recognition for different clothing types
- Real-time similarity matching
- File upload and URL-based search methods
- Responsive web interface

### Computer Vision
- Shape-based matching prioritizing garment structure
- 50-dimensional visual feature extraction
- Category-aware similarity matching
- Optimized for fashion product classification

### Technical Implementation
- FastAPI backend with automatic documentation
- JavaScript frontend with modern UI
- Vector-based similarity computation
- Comprehensive error handling

## Quick Start

### Using the Live Application
1. Visit [https://visual-product-matcher-xi.vercel.app](https://visual-product-matcher-xi.vercel.app)
2. Upload an image or provide a URL of a fashion product
3. Adjust similarity threshold if needed
4. Click "Find Similar Products" to see results

### Local Development Setup

#### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend development)
- Git

#### Backend Setup
```bash
# Clone the repository
git clone https://github.com/kavyaaaaaa/Visual-Product-Matcher.git
cd Visual-Product-Matcher-Deploy

# Install dependencies
pip install -r backend/requirements.txt

# Run the backend server
python backend/main.py
```

The API will be available at `http://localhost:8000`

#### Frontend Setup
```bash
# Navigate to frontend directory (if not already there)
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

## Architecture

### Backend Components
- FastAPI web framework
- Image processing pipeline for feature extraction
- Similarity engine with weighted cosine similarity
- JSON database for product data and visual embeddings

### Frontend Components
- JavaScript interface
- Responsive design
- Image upload and URL validation
- Product card grid with similarity scores

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /api/search/upload` - Upload image search
- `POST /api/search/url` - URL image search
- `GET /api/categories` - Available categories

### Example API Usage
```bash
# Health check
curl https://visual-product-matcher-p5u4.onrender.com/health

# Image upload search
curl -X POST "https://visual-product-matcher-p5u4.onrender.com/api/search/upload" \
  -F "file=@image.jpg" \
  -F "min_similarity=0.3"

# URL search
curl -X POST "https://visual-product-matcher-p5u4.onrender.com/api/search/url" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg", "min_similarity": 0.3}'
```

## Configuration

### Environment Variables

**Backend (.env)**
```
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key  # Optional
IMAGE_DIRECTORY=./images
PORT=8000
```
