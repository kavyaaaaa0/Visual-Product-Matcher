#!/bin/bash

# 🔐 Secure Environment Setup for Visual Product Matcher
# This script sets up your environment variables securely

set -e

echo "🔐 Setting up secure environment for Visual Product Matcher..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env.template exists
if [ ! -f ".env.template" ]; then
    print_error ".env.template not found! Please ensure you're in the project root."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.template .env
    print_warning "Please edit .env file and add your actual API keys"
    print_warning "See SECURITY_SETUP.md for your API keys"
else
    print_status ".env file already exists"
fi

# Set up API keys securely
print_status "Setting up API keys..."

# Store API keys in environment variables
export GOOGLE_API_KEY="AIzaSyBHzHoRuOjxnwXE9zpZ7rwm04BurYOwxsM"
export PINECONE_API_KEY="pcsk_2pgosH_6jD5aPkf8ohLS5cZBGed1simWicJEcfv1ssGXw19n9Xk8AAygHQ3KotHqsSU5aw"

# Update .env file with actual keys (for local development only)
cat > .env << EOF
# Visual Product Matcher - Environment Variables
# IMPORTANT: This file contains sensitive API keys - never commit to version control

# Google AI Studio API Configuration
GOOGLE_API_KEY=$GOOGLE_API_KEY

# Pinecone Configuration  
PINECONE_API_KEY=$PINECONE_API_KEY

# Dataset Processing Configuration
MAX_IMAGES_TO_PROCESS=100

# Production Configuration
IMAGE_DIRECTORY=./images
PORT=8000
HOST=0.0.0.0
EOF

print_status "✅ Environment variables configured successfully!"

# Verify .env is in .gitignore
if grep -q "^\.env$" .gitignore; then
    print_status "✅ .env is properly ignored by git"
else
    print_warning "Adding .env to .gitignore for security"
    echo ".env" >> .gitignore
fi

echo ""
echo "🔐 Security Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Your API keys are now configured locally"
echo "2. For deployment, manually add keys to hosting dashboards:"
echo "   - Render: Dashboard → Environment Variables"
echo "   - Vercel: Project Settings → Environment Variables"
echo "3. See SECURITY_SETUP.md for the actual key values"
echo ""
echo "⚠️  IMPORTANT: Never commit the .env file to version control!"
echo "✅ The .env file is automatically ignored by git"
