# Alternative Render Deployment Guide (Manual Service Creation)

If you're getting Docker-related errors with the render.yaml Blueprint approach, you can deploy each service individually:

## Option 1: Individual Service Deployment (Recommended)

### Deploy Backend Service

1. **Go to Render Dashboard** → Click "New" → "Web Service"
2. **Connect GitHub** → Select your repository
3. **Configure Backend Service**:
   - **Name**: `acta-diurna-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Auto-Deploy**: Yes

4. **Environment Variables**:
   - `MONGO_URL`: Your MongoDB Atlas connection string
   - `SECRET_KEY`: Generate a random string (or let Render auto-generate)
   - `ENVIRONMENT`: `production`

### Deploy Frontend Service

1. **Go to Render Dashboard** → Click "New" → "Web Service"
2. **Connect GitHub** → Select your repository
3. **Configure Frontend Service**:
   - **Name**: `acta-diurna-frontend`
   - **Environment**: `Node`
   - **Build Command**: `cd frontend && yarn install && yarn build`
   - **Start Command**: `cd frontend && npx serve -s build -l $PORT`
   - **Auto-Deploy**: Yes

4. **Environment Variables**:
   - `REACT_APP_BACKEND_URL`: `https://acta-diurna-backend.onrender.com/api` (use your actual backend URL)
   - `NODE_ENV`: `production`

## Option 2: Docker Deployment (If needed)

If native buildpacks don't work, you can use the Dockerfiles I created:

### Backend Docker Service
- **Environment**: `Docker`
- **Dockerfile Path**: `backend/Dockerfile`
- **Docker Context Directory**: `.` (root)

### Frontend Docker Service
- **Environment**: `Docker`  
- **Dockerfile Path**: `frontend/Dockerfile`
- **Docker Context Directory**: `.` (root)

## Option 3: Simplified render.yaml

Try this minimal render.yaml:

```yaml
services:
  - name: acta-diurna-backend
    type: web
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
    
  - name: acta-diurna-frontend
    type: web
    env: node
    buildCommand: cd frontend && yarn install && yarn build
    startCommand: cd frontend && npx serve -s build -l $PORT
```

Then set environment variables manually in Render dashboard.

## Troubleshooting Tips

1. **Clear render.yaml issues**: Delete render.yaml and deploy services individually
2. **Path issues**: Make sure your GitHub repo has the correct folder structure
3. **Build command issues**: Test build commands locally first
4. **Environment variables**: Set them in Render dashboard after service creation

Choose the approach that works best for your deployment!