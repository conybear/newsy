# Acta Diurna - Deployment Guide

## 🚀 Deployment Status: READY

This Flask application is fully configured for Emergent platform deployment.

## 📋 Build Process

### Frontend Build System
- **Build Script**: `frontend/build.js` - Creates dummy frontend build for deployment compatibility
- **Output Directory**: `/app/build/` - Required by Emergent/Kaniko deployment system
- **Build Command**: `cd frontend && yarn build`

### Required Build Files
The deployment system requires these files in `/app/build/`:
- ✅ `index.html` - Redirect page to Flask app
- ✅ `manifest.json` - PWA manifest  
- ✅ `asset-manifest.json` - Asset mapping
- ✅ `static/css/main.css` - Placeholder CSS
- ✅ `static/js/main.js` - Placeholder JavaScript

## 🔧 Technical Architecture

### Application Type
- **Framework**: Flask (Python)
- **Storage**: In-memory (no database required)
- **Server**: Gunicorn for production
- **Port**: Configurable via `PORT` environment variable

### Key Files
- `app.py` - Main Flask application
- `Procfile` - Gunicorn configuration (`web: gunicorn app:app`)
- `requirements.txt` - Python dependencies
- `templates/index.html` - Main HTML template

## 🌐 Environment Variables

### Required for Email Features
- `SENDER_EMAIL` - Email address for newsletters
- `SENDER_PASSWORD` - Email app password

### Optional
- `PORT` - Application port (defaults to 5000)

## ✅ Pre-Deployment Checklist

1. **Build Directory**: ✅ `/app/build/` exists with all required files
2. **Flask App**: ✅ Imports successfully
3. **Gunicorn**: ✅ Compatible and tested
4. **Dependencies**: ✅ All listed in requirements.txt
5. **Environment**: ✅ PORT variable handling implemented

## 🧪 Verification Commands

```bash
# Verify build process
cd frontend && yarn build

# Verify build output
node verify-build.js

# Test Flask import
python -c "import app; print('Flask app imports successfully')"

# Test with Gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

## 🎯 Deployment Notes

- **Database**: None required (uses in-memory storage)
- **Build Process**: Creates dummy frontend build for platform compatibility
- **URL Structure**: Flask serves all routes, build files are for deployment system only
- **Platform**: Optimized for Emergent deployment with Kaniko builder

## 🔄 Previous Issues Resolved

- ✅ "Command not found" build errors - Fixed with Node.js build script
- ✅ Missing `/app/build` directory - Now created by robust build process  
- ✅ Supervisor configuration - Updated for Flask instead of FastAPI+React
- ✅ Preview site startup - Flask now runs on expected port

---

**Status**: 🟢 Ready for Production Deployment