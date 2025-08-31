# Visual Product Matcher

🔍 **AI-powered visual similarity search for fashion products using advanced computer vision**

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://visual-product-matcher-xi.vercel.app)
[![Backend API](https://img.shields.io/badge/API-Docs-blue)](https://visual-product-matcher-p5u4.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌐 Live Deployments

- **🎯 Frontend Application**: [https://visual-product-matcher-xi.vercel.app](https://visual-product-matcher-xi.vercel.app)
- **⚡ Backend API**: [https://visual-product-matcher-p5u4.onrender.com](https://visual-product-matcher-p5u4.onrender.com)
- **📚 API Documentation**: [https://visual-product-matcher-p5u4.onrender.com/docs](https://visual-product-matcher-p5u4.onrender.com/docs)

## ✨ Features

### 🎯 Core Functionality
- **Advanced Visual Search**: Upload images or provide URLs to find similar fashion products
- **Smart Garment Recognition**: Distinguishes between different clothing types (trousers, dresses, tops, etc.)
- **Real-time Processing**: Fast similarity matching with optimized algorithms
- **Multiple Input Methods**: Support for file uploads and URL-based searches
- **Responsive Design**: Works seamlessly across desktop and mobile devices

### 🧠 AI & Computer Vision
- **Shape-based Matching**: Prioritizes garment silhouette and structure over color
- **Advanced Feature Extraction**: 50-dimensional visual embeddings capturing:
  - Garment shape and aspect ratio
  - Structural patterns and edges
  - Texture analysis
  - Color features (with reduced importance)
- **Category-aware Similarity**: Optimized matching within clothing categories

### 🛠️ Technical Highlights
- **FastAPI Backend**: High-performance async API with automatic documentation
- **Modern Frontend**: Clean, intuitive interface built with vanilla JavaScript
- **Vector-based Search**: Efficient similarity computation using cosine distance
- **Error Handling**: Comprehensive error management and user feedback
- **CORS Support**: Cross-origin resource sharing for web integration

## 🚀 Quick Start

### 📱 Using the Live Application
1. Visit [https://visual-product-matcher-xi.vercel.app](https://visual-product-matcher-xi.vercel.app)
2. Upload an image or provide a URL of a fashion product
3. Adjust similarity threshold if needed
4. Click "Find Similar Products" to see results

### 🔧 Local Development Setup

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

## 🏛️ Architecture

### Backend Components
- **FastAPI**: High-performance Python web framework
- **Image Processing Pipeline**: Advanced computer vision for feature extraction
- **Similarity Engine**: Weighted cosine similarity for garment matching
- **JSON Database**: Optimized storage of product data and visual embeddings

### Frontend Components
- **Modern JavaScript**: Clean, efficient UI implementation
- **Responsive Design**: Mobile-first approach with CSS flexbox/grid
- **Preview System**: Real-time image upload and URL validation
- **Results Display**: Interactive product card grid with similarity scores

## 🔑 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /api/search/upload` - Upload image search
- `POST /api/search/url` - URL image search
- `GET /api/categories` - Available categories

### Pinecone Endpoints (Optional)
- `GET /api/pinecone/stats` - Vector database stats
- `POST /api/pinecone/initialize` - Initialize Pinecone

### Example API Usage
```bash
# Health check
curl https://visual-product-matcher-backend.onrender.com/health

# Image upload search
curl -X POST "https://visual-product-matcher-backend.onrender.com/api/search/upload" \
  -F "file=@image.jpg" \
  -F "min_similarity=0.3"

# URL search
curl -X POST "https://visual-product-matcher-backend.onrender.com/api/search/url" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg", "min_similarity": 0.3}'
```

## 🛠️ Development

### Local Development
```bash
# Backend
cd backend
source venv/bin/activate
python main.py

# Frontend (in another terminal)
cd frontend  
npm start
```

### Adding New Products
1. Add images to `data_processing/dataset/Images/Images/`
2. Update product database JSON
3. Run migration script (if using Pinecone)

## 📈 Performance & Scaling

### Current Capacity
- **Free Tier**: 100 products (~100MB)
- **Optimized**: 1000 products (~1GB)
- **Pinecone**: Unlimited products

### Response Times
- **Local Search**: ~200ms
- **Pinecone Search**: ~50ms
- **Image Processing**: ~100ms

## 🔒 Security

- Environment variables for API keys
- CORS configuration
- Input validation
- Error sanitization

## 🐛 Troubleshooting

### Common Issues

**"Failed to connect to backend"**
- Check if backend is deployed and running
- Verify REACT_APP_API_URL in frontend

**"Image not loading"**
- Check image paths in database
- Verify image directory mounting

**"Slow search performance"**
- Consider migrating to Pinecone
- Check dataset size

### Debug Mode
Enable debug logging by setting environment variable:
```bash
LOG_LEVEL=DEBUG
```

## 📝 Configuration

### Environment Variables

**Backend (.env)**
```
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key  # Optional
IMAGE_DIRECTORY=./images
PORT=8000
```

**Frontend (.env)**
```
REACT_APP_API_URL=http://localhost:8000  # Development
# Production URL set via vercel.json
```

## 🔄 Migration to Pinecone (Optional)

For better performance and scalability:

```bash
cd backend
python migrate_to_pinecone.py
```

This will:
1. Generate better embeddings using MobileNetV2
2. Upload vectors to Pinecone
3. Enable faster similarity search

## 📞 Support

If you encounter issues:
1. Check the deployment logs on Render/Vercel
2. Verify environment variables
3. Test API endpoints directly
4. Check browser console for frontend errors

## 🎯 Next Steps

1. **Immediate**: Deploy with current setup
2. **Week 1**: Set up Pinecone for better performance  
3. **Week 2**: Add more products and categories
4. **Month 1**: Implement advanced features (filters, recommendations)

---

**Happy Deploying!** 🚀
