#!/bin/bash

# Create build directory structure
mkdir -p build/static/js
mkdir -p build/static/css
mkdir -p build/static/media

# Create main HTML file
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
cat > build/static/css/main.css << 'EOF'
/* Placeholder CSS file for deployment compatibility */
body { font-family: Arial, sans-serif; }
EOF

# Create main JS file
cat > build/static/js/main.js << 'EOF'
// Placeholder JS file for deployment compatibility
console.log('Flask app loaded');
EOF

# Create manifest.json
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

echo "Build completed successfully"