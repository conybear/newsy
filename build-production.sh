#!/bin/bash
set -e

echo "==============================================="
echo "🏗️  ACTA DIURNA PRODUCTION BUILD SCRIPT"
echo "==============================================="

# Log current environment
echo "📍 Current directory: $(pwd)"
echo "🌐 Environment: ${NODE_ENV:-development}"
echo "📦 Node version: $(node --version 2>/dev/null || echo 'Node not found')"
echo "🧶 Yarn version: $(yarn --version 2>/dev/null || echo 'Yarn not found')"

# Create build directory structure first
echo "📁 Creating build directory structure..."
mkdir -p /app/build/static/{js,css,media}
echo "✅ Build directory structure created"

# Change to frontend directory and install dependencies
echo "📥 Installing frontend dependencies..."
cd /app/frontend
yarn install --frozen-lockfile --non-interactive
echo "✅ Dependencies installed"

# Run the build process
echo "🔨 Running build process..."
yarn build
echo "✅ Build process completed"

# Verify build output exists
echo "🔍 Verifying build output..."
cd /app
if [ ! -d "build" ]; then
    echo "❌ ERROR: Build directory not found"
    exit 1
fi

# Check required files
required_files=("build/index.html" "build/manifest.json" "build/asset-manifest.json")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ ERROR: Required file missing: $file"
        exit 1
    fi
    file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
    echo "✅ $file ($file_size bytes)"
done

# List final build structure
echo "📋 Final build structure:"
find build -type f | sort | while read -r file; do
    file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
    echo "  📄 $file ($file_size bytes)"
done

echo "==============================================="
echo "🎉 BUILD COMPLETED SUCCESSFULLY!"
echo "📁 Build output: /app/build"
echo "🚀 Ready for deployment!"
echo "==============================================="