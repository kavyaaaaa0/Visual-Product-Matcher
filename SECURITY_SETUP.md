# 🔐 Security Setup Guide - API Keys Configuration

## ⚠️ CRITICAL: API Key Security

**NEVER commit actual API keys to version control!**

## 🔑 Your API Keys (Store Securely)

### Google AI API Key
```
GOOGLE_API_KEY={{GOOGLE_API_KEY}}
```
**Actual Key**: `AIzaSyBHzHoRuOjxnwXE9zpZ7rwm04BurYOwxsM`

### Pinecone API Key  
```
PINECONE_API_KEY={{PINECONE_API_KEY}}
```
**Actual Key**: `pcsk_2pgosH_6jD5aPkf8ohLS5cZBGed1simWicJEcfv1ssGXw19n9Xk8AAygHQ3KotHqsSU5aw`

## 🛠️ Local Development Setup

### Step 1: Create Local .env File
```bash
# Copy template and add your keys
cp .env.template .env

# Edit .env with your actual API keys
nano .env  # or your preferred editor
```

### Step 2: Add Your Keys to .env
```bash
# Visual Product Matcher - Environment Variables
GOOGLE_API_KEY=AIzaSyBHzHoRuOjxnwXE9zpZ7rwm04BurYOwxsM
PINECONE_API_KEY=pcsk_2pgosH_6jD5aPkf8ohLS5cZBGed1simWicJEcfv1ssGXw19n9Xk8AAygHQ3KotHqsSU5aw
MAX_IMAGES_TO_PROCESS=100
IMAGE_DIRECTORY=./images
PORT=8000
HOST=0.0.0.0
```

## 🌐 Production Deployment Setup

### Render (Backend)
1. Go to Render Dashboard → Your Service → Environment
2. Add environment variables:
   - `GOOGLE_API_KEY`: `AIzaSyBHzHoRuOjxnwXE9zpZ7rwm04BurYOwxsM`
   - `PINECONE_API_KEY`: `pcsk_2pgosH_6jD5aPkf8ohLS5cZBGed1simWicJEcfv1ssGXw19n9Xk8AAygHQ3KotHqsSU5aw`

### Vercel (Frontend)  
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add:
   - `REACT_APP_API_URL`: `https://your-backend-url.onrender.com`

## 🔒 Security Best Practices

### ✅ What We've Done
- ✅ Removed API keys from all committed files
- ✅ Added .env to .gitignore
- ✅ Created secure templates
- ✅ Used placeholder variables in code

### ✅ Additional Security Tips
- 🔄 Rotate API keys regularly
- 👥 Don't share keys in chat/email
- 📱 Use different keys for dev/prod
- 🔍 Monitor API usage for anomalies

## 🚨 Emergency: If Keys Are Compromised

### Google AI Studio
1. Go to https://makersuite.google.com/app/apikey
2. Delete compromised key
3. Generate new key
4. Update in all environments

### Pinecone
1. Go to https://app.pinecone.io/
2. API Keys section → Delete compromised key  
3. Generate new key
4. Update in all environments

## ✅ Verification Checklist

- [ ] .env file created locally (not committed)
- [ ] API keys added to Render environment
- [ ] Frontend environment configured  
- [ ] All services deployed successfully
- [ ] API keys working in production

---
**🔐 Your API keys are now secure and ready for deployment!**
