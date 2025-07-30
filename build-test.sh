#!/bin/bash

# Acta Diurna - Local Production Build Test Script

echo "🚀 Building Acta Diurna for Production..."
echo "========================================"

# Test Backend Dependencies
echo "📦 Testing Backend Dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Backend dependency installation failed"
    exit 1
fi
echo "✅ Backend dependencies installed successfully"

# Test Frontend Build
echo "📦 Testing Frontend Build..."
cd ../frontend
yarn install
if [ $? -ne 0 ]; then
    echo "❌ Frontend dependency installation failed"
    exit 1
fi

yarn build
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi
echo "✅ Frontend build completed successfully"

cd ..

echo ""
echo "🎉 Production Build Test Completed Successfully!"
echo "================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Push your code to GitHub"
echo "2. Set up MongoDB Atlas cluster"
echo "3. Deploy to Render using render.yaml"
echo "4. Configure environment variables in Render dashboard"
echo "5. Test the deployed application"
echo ""
echo "📚 See DEPLOYMENT.md for detailed deployment instructions"