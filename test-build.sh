#!/bin/bash
set -e

echo "🧪 Testing build process for deployment readiness..."

# Clean slate
rm -rf build

# Run the frontend build command (as Emergent would)
cd frontend
yarn build
cd ..

# Verify all expected files exist
echo "✅ Verifying required files exist..."
required_files=(
    "build/index.html"
    "build/asset-manifest.json" 
    "build/manifest.json"
    "build/static/css/main.css"
    "build/static/js/main.js"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ CRITICAL: $file is missing!"
        exit 1
    else
        echo "✅ $file exists"
    fi
done

# Verify directory structure
required_dirs=(
    "build/static/js"
    "build/static/css"
    "build/static/media"
)

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ CRITICAL: $dir directory is missing!"
        exit 1
    else
        echo "✅ $dir directory exists"
    fi
done

echo ""
echo "🎉 BUILD TEST PASSED - All requirements met for Emergent deployment!"
echo "📁 Build output ready at: /app/build"