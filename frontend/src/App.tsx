import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import './App.css';

interface ProductResult {
  product_id: string;
  product_name: string;
  category: string;
  image_path: string;
  similarity_score: number;
}

interface SearchResponse {
  query_method: string;
  total_results: number;
  results: ProductResult[];
  processing_time: number;
}

function App() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [searchResults, setSearchResults] = useState<ProductResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [minSimilarity, setMinSimilarity] = useState<number>(0.3);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [searchMethod, setSearchMethod] = useState<'upload' | 'url'>('upload');
  const [processingTime, setProcessingTime] = useState<number>(0);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setImageFile(file);
      setImageUrl('');
      setPreviewUrl(URL.createObjectURL(file));
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024
  });

  const handleImageUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setImageUrl(url);
    setImageFile(null);
    
    if (url && url.trim() !== '') {
      // Validate URL format
      try {
        new URL(url);
        setPreviewUrl(url);
        setError('');
      } catch {
        setPreviewUrl('');
        if (url.length > 10) {
          setError('Please enter a valid image URL');
        }
      }
    } else {
      setPreviewUrl('');
      setError('');
    }
  };

  const searchByUpload = async () => {
    if (!imageFile) {
      setError('Please select an image file');
      return;
    }

    setLoading(true);
    setError('');
    setSearchResults([]);

    const formData = new FormData();
    formData.append('file', imageFile);

    try {
      console.log('Sending request to:', `${API_BASE_URL}/api/search/upload`);
      console.log('File details:', { name: imageFile.name, size: imageFile.size, type: imageFile.type });
      
      const response = await axios.post<SearchResponse>(
        `${API_BASE_URL}/api/search/upload?min_similarity=${minSimilarity}&max_results=12`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000, // 30 second timeout
        }
      );

      console.log('Search response:', response.data);
      setSearchResults(response.data.results);
      setProcessingTime(response.data.processing_time);
    } catch (err: any) {
      console.error('Search error:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.message || 
                          'Failed to search for similar products';
      setError(errorMessage);
      
      // Additional error details
      if (err.code === 'ECONNREFUSED') {
        setError('Cannot connect to the backend server. Please ensure the API is running on ' + API_BASE_URL);
      } else if (err.response?.status === 503) {
        setError('Backend service unavailable. The product database may not be loaded.');
      }
    } finally {
      setLoading(false);
    }
  };

  const searchByUrl = async () => {
    if (!imageUrl) {
      setError('Please enter an image URL');
      return;
    }

    setLoading(true);
    setError('');
    setSearchResults([]);

    try {
      console.log('Sending URL search request to:', `${API_BASE_URL}/api/search/url`);
      console.log('Image URL:', imageUrl);
      
      const response = await axios.post<SearchResponse>(
        `${API_BASE_URL}/api/search/url`,
        {
          image_url: imageUrl,
          min_similarity: minSimilarity,
          max_results: 12
        },
        {
          timeout: 30000, // 30 second timeout
        }
      );

      console.log('URL search response:', response.data);
      setSearchResults(response.data.results);
      setProcessingTime(response.data.processing_time);
    } catch (err: any) {
      console.error('URL search error:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.message || 
                          'Failed to search for similar products';
      setError(errorMessage);
      
      // Additional error details
      if (err.code === 'ECONNREFUSED') {
        setError('Cannot connect to the backend server. Please ensure the API is running on ' + API_BASE_URL);
      } else if (err.response?.status === 503) {
        setError('Backend service unavailable. The product database may not be loaded.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchMethod === 'upload') {
      searchByUpload();
    } else {
      searchByUrl();
    }
  };

  const formatSimilarity = (score: number) => {
    return `${(score * 100).toFixed(1)}%`;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Visual Product Matcher</h1>
        <p>Find visually similar fashion products using AI</p>
      </header>

      <main className="App-main">
        {/* Search Method Toggle */}
        <div className="method-toggle">
          <button 
            className={`method-btn ${searchMethod === 'upload' ? 'active' : ''}`}
            onClick={() => {
              setSearchMethod('upload');
              setImageUrl('');
              if (imageFile) {
                setPreviewUrl(URL.createObjectURL(imageFile));
              } else {
                setPreviewUrl('');
              }
            }}
          >
            Upload Image
          </button>
          <button 
            className={`method-btn ${searchMethod === 'url' ? 'active' : ''}`}
            onClick={() => {
              setSearchMethod('url');
              setImageFile(null);
              if (imageUrl && imageUrl.trim() !== '') {
                setPreviewUrl(imageUrl);
              } else {
                setPreviewUrl('');
              }
            }}
          >
            Image URL
          </button>
        </div>

        {/* Upload Section */}
        {searchMethod === 'upload' && (
          <section className="upload-section">
            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
              <input {...getInputProps()} />
              {isDragActive ? (
                <p>Drop your image here...</p>
              ) : (
                <div>
                  <p>Drag & drop an image here, or click to select</p>
                  <small>Supported formats: JPEG, PNG, GIF, WebP (max 10MB)</small>
                  {imageFile && (
                    <div style={{marginTop: '10px', color: '#28a745'}}>
                      Selected: {imageFile.name}
                    </div>
                  )}
                </div>
              )}
            </div>
          </section>
        )}

        {/* URL Section */}
        {searchMethod === 'url' && (
          <section className="url-section">
            <div className="url-input-container">
              <input
                type="text"
                placeholder="Enter image URL (e.g., https://example.com/image.jpg)..."
                value={imageUrl}
                onChange={handleImageUrlChange}
                className="url-input"
              />
              {imageUrl && (
                <small style={{display: 'block', marginTop: '5px', color: '#666'}}>
                  URL entered: {imageUrl.length > 50 ? imageUrl.substring(0, 50) + '...' : imageUrl}
                </small>
              )}
            </div>
          </section>
        )}

        {/* Preview Section */}
        {previewUrl && (
          <section className="preview-section">
            <h3>Query Image</h3>
            <img 
              src={previewUrl} 
              alt="Query" 
              className="preview-image"
              onError={(e) => {
                console.error('Failed to load preview image:', previewUrl);
                setError('Failed to load image from URL. Please check the URL and try again.');
                setPreviewUrl('');
              }}
              onLoad={() => {
                console.log('Preview image loaded successfully:', previewUrl);
                setError('');
              }}
            />
          </section>
        )}

        {/* Controls */}
        <section className="controls-section">
          <div className="similarity-control">
            <label htmlFor="similarity-slider">Minimum Similarity: {formatSimilarity(minSimilarity)}</label>
            <input
              id="similarity-slider"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={minSimilarity}
              onChange={(e) => setMinSimilarity(parseFloat(e.target.value))}
              className="similarity-slider"
            />
          </div>
          
          <button 
            onClick={handleSearch} 
            disabled={loading || (!imageFile && !imageUrl)}
            className="search-btn"
          >
            {loading ? 'Searching...' : 'Find Similar Products'}
          </button>
        </section>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Analyzing image and finding similar products...</p>
          </div>
        )}

        {/* Results Section */}
        {searchResults.length > 0 && (
          <section className="results-section">
            <div className="results-header">
              <h2>Similar Products Found</h2>
              <p>{searchResults.length} results • Processing time: {processingTime.toFixed(2)}s</p>
            </div>
            
            <div className="results-grid">
              {searchResults.map((product) => (
                <div key={product.product_id} className="product-card">
                  <div className="product-image-container">
                    <img 
                      src={`${API_BASE_URL}/images/${product.image_path.split('/').pop()}`}
                      alt={product.product_name}
                      className="product-image"
                      onError={(e) => {
                        console.error('Failed to load image:', `${API_BASE_URL}/images/${product.image_path.split('/').pop()}`);
                        // Fallback to placeholder if image fails to load
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        target.nextElementSibling?.classList.remove('hidden');
                      }}
                    />
                    <div className="product-placeholder hidden">
                      <span>IMG</span>
                      <small>Image not available</small>
                    </div>
                    <div className="similarity-badge">
                      {formatSimilarity(product.similarity_score)}
                    </div>
                  </div>
                  <div className="product-info">
                    <h4>{product.product_name}</h4>
                    <p className="product-category">{product.category}</p>
                    <p className="product-id">ID: {product.product_id}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
