// Configuration
const API_BASE_URL = 'https://visual-product-matcher-p5u4.onrender.com';

// State
let currentSearchMethod = 'upload';
let selectedFile = null;
let imageUrl = '';

// DOM Elements
const uploadBtn = document.getElementById('upload-btn');
const urlBtn = document.getElementById('url-btn');
const uploadSection = document.getElementById('upload-section');
const urlSection = document.getElementById('url-section');
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const imageUrlInput = document.getElementById('image-url');
const previewSection = document.getElementById('preview-section');
const previewImage = document.getElementById('preview-image');
const similaritySlider = document.getElementById('similarity-slider');
const similarityValue = document.getElementById('similarity-value');
const searchBtn = document.getElementById('search-btn');
const errorMessage = document.getElementById('error-message');
const loadingState = document.getElementById('loading-state');
const resultsSection = document.getElementById('results-section');
const resultsInfo = document.getElementById('results-info');
const resultsGrid = document.getElementById('results-grid');

// Event Listeners
uploadBtn.addEventListener('click', () => switchMethod('upload'));
urlBtn.addEventListener('click', () => switchMethod('url'));

// File upload
dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', handleDragOver);
dropzone.addEventListener('dragleave', handleDragLeave);
dropzone.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);

// URL input
imageUrlInput.addEventListener('input', handleUrlInput);

// Similarity slider
similaritySlider.addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    similarityValue.textContent = `${value}.0%`;
});

// Search button
searchBtn.addEventListener('click', handleSearch);

// Functions
function switchMethod(method) {
    currentSearchMethod = method;
    
    // Update button states
    uploadBtn.classList.toggle('active', method === 'upload');
    urlBtn.classList.toggle('active', method === 'url');
    
    // Show/hide sections
    uploadSection.classList.toggle('hidden', method !== 'upload');
    urlSection.classList.toggle('hidden', method !== 'url');
    
    // Clear previous inputs and reset
    if (method === 'upload') {
        imageUrl = '';
        imageUrlInput.value = '';
        updatePreview();
    } else {
        selectedFile = null;
        fileInput.value = '';
        updatePreview();
    }
}

function handleDragOver(e) {
    e.preventDefault();
    dropzone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropzone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    // Validate file
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file.');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB.');
        return;
    }
    
    selectedFile = file;
    updatePreview();
    hideError();
}

function handleUrlInput(e) {
    imageUrl = e.target.value.trim();
    updatePreview();
}

function updatePreview() {
    if (currentSearchMethod === 'upload' && selectedFile) {
        const url = URL.createObjectURL(selectedFile);
        previewImage.src = url;
        previewSection.classList.remove('hidden');
        searchBtn.disabled = false;
        
        // Update dropzone content
        const dropzoneContent = dropzone.querySelector('.dropzone-content');
        dropzoneContent.innerHTML = `
            <p style="color: #28a745;">✓ ${selectedFile.name}</p>
            <small>Click to change or drag another file</small>
        `;
    } else if (currentSearchMethod === 'url' && imageUrl) {
        // Validate URL format
        try {
            new URL(imageUrl);
            previewImage.src = imageUrl;
            previewImage.onload = () => {
                previewSection.classList.remove('hidden');
                searchBtn.disabled = false;
                hideError();
            };
            previewImage.onerror = () => {
                showError('Failed to load image from URL. Please check the URL.');
                previewSection.classList.add('hidden');
                searchBtn.disabled = true;
            };
        } catch {
            previewSection.classList.add('hidden');
            searchBtn.disabled = true;
            if (imageUrl.length > 10) {
                showError('Please enter a valid URL.');
            }
        }
    } else {
        previewSection.classList.add('hidden');
        searchBtn.disabled = true;
        
        if (currentSearchMethod === 'upload') {
            // Reset dropzone content
            const dropzoneContent = dropzone.querySelector('.dropzone-content');
            dropzoneContent.innerHTML = `
                <p>Drag & drop an image here, or click to select</p>
                <small>Supported formats: JPEG, PNG, GIF, WebP (max 10MB)</small>
            `;
        }
    }
}

async function handleSearch() {
    if (!selectedFile && !imageUrl) {
        showError('Please select an image or enter an image URL.');
        return;
    }
    
    hideError();
    showLoading(true);
    hideResults();
    
    try {
        const minSimilarity = parseInt(similaritySlider.value) / 100;
        const maxResults = 12;
        
        let response;
        
        if (currentSearchMethod === 'upload') {
            response = await searchByUpload(selectedFile, minSimilarity, maxResults);
        } else {
            response = await searchByUrl(imageUrl, minSimilarity, maxResults);
        }
        
        displayResults(response);
        
    } catch (error) {
        console.error('Search error:', error);
        showError(error.message || 'Failed to search for similar products. Please try again.');
    } finally {
        showLoading(false);
    }
}

async function searchByUpload(file, minSimilarity, maxResults) {
    const formData = new FormData();
    formData.append('file', file);
    
    const url = `${API_BASE_URL}/api/search/upload?min_similarity=${minSimilarity}&max_results=${maxResults}`;
    
    const response = await fetch(url, {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

async function searchByUrl(imageUrl, minSimilarity, maxResults) {
    const url = `${API_BASE_URL}/api/search/url`;
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_url: imageUrl,
            min_similarity: minSimilarity,
            max_results: maxResults
        }),
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

function displayResults(data) {
    const { results, processing_time, total_results } = data;
    
    // Update results info
    resultsInfo.textContent = `${total_results} results • Processing time: ${processing_time.toFixed(2)}s`;
    
    // Clear previous results
    resultsGrid.innerHTML = '';
    
    // Display results
    results.forEach(product => {
        const productCard = createProductCard(product);
        resultsGrid.appendChild(productCard);
    });
    
    // Show results section
    resultsSection.classList.remove('hidden');
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const similarity = (product.similarity_score * 100).toFixed(1);
    const imageUrl = `${API_BASE_URL}/images/${product.image_path.split('/').pop()}`;
    
    card.innerHTML = `
        <div class="product-image-container">
            <img 
                src="${imageUrl}" 
                alt="${product.product_name}" 
                class="product-image"
                onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
            >
            <div class="product-placeholder" style="display: none;">
                <span>IMG</span>
                <small>Image not available</small>
            </div>
            <div class="similarity-badge">${similarity}%</div>
        </div>
        <div class="product-info">
            <h4>${product.product_name}</h4>
            <p class="product-category">${product.category}</p>
            <p class="product-id">ID: ${product.product_id}</p>
        </div>
    `;
    
    return card;
}

function showError(message) {
    errorMessage.textContent = `Error: ${message}`;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

function showLoading(show) {
    loadingState.classList.toggle('hidden', !show);
    searchBtn.disabled = show;
}

function hideResults() {
    resultsSection.classList.add('hidden');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Visual Product Matcher initialized');
    console.log('API Base URL:', API_BASE_URL);
});
