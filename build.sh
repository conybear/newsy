#!/bin/bash
set -e  # Exit immediately if any command fails

# Build frontend assets for Emergent/kaniko deployment compatibility
# This script creates /app/build directory as required by the deployment system
echo "Starting build process..."

# Clean any existing build directory to ensure fresh build
rm -rf build

# Create build directory structure
echo "Creating build directory structure..."
mkdir -p build/static/js
mkdir -p build/static/css
mkdir -p build/static/media

# Create main HTML file
echo "Creating index.html..."
cat > build/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Flask App Redirect</title>
    <meta http-equiv="refresh" content="0; url=/">
</head>
<body>
    <p>Redirecting to Flask app...</p>
    <script>window.location.href = '/';</script>
</body>
</html>
EOF

# Create main CSS file
echo "Creating main.css..."
cat > build/static/css/main.css << 'EOF'
/* Placeholder CSS file for deployment compatibility */
body { font-family: Arial, sans-serif; }
EOF

# Create main JS file
echo "Creating main.js..."
cat > build/static/js/main.js << 'EOF'
// Placeholder JS file for deployment compatibility
console.log('Flask app loaded');
EOF

# Create manifest.json
echo "Creating manifest.json..."
cat > build/manifest.json << 'EOF'
{
  "short_name": "Acta Diurna",
  "name": "Acta Diurna - Personal Daily Chronicle",
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#f59e0b",
  "background_color": "#ffffff"
}
EOF

# Create asset-manifest.json
echo "Creating asset-manifest.json..."
cat > build/asset-manifest.json << 'EOF'
{
  "files": {
    "main.css": "/static/css/main.css",
    "main.js": "/static/js/main.js",
    "index.html": "/index.html"
  },
  "entrypoints": [
    "static/css/main.css",
    "static/js/main.js"
  ]
}
EOF

# Ensure all required files exist - CRITICAL for deployment success
echo "Verifying all required files are created..."
for file in build/index.html build/asset-manifest.json build/manifest.json build/static/css/main.css build/static/js/main.js; do
  [ -f "$file" ] || { echo "CRITICAL ERROR: $file missing"; exit 1; }
done

# Verify directory structure
[ -d "build/static/js" ] || { echo "CRITICAL ERROR: build/static/js directory missing"; exit 1; }
[ -d "build/static/css" ] || { echo "CRITICAL ERROR: build/static/css directory missing"; exit 1; }
[ -d "build/static/media" ] || { echo "CRITICAL ERROR: build/static/media directory missing"; exit 1; }

# Final verification
echo "Build verification complete. Files created:"
ls -la build/
ls -la build/static/

echo "✅ Build completed successfully - all required files present"
echo "📁 Output directory: /app/build (required by Emergent/kaniko deployment system)"