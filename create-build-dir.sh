#!/bin/bash
# Emergency build directory creation script
echo "Creating /app/build directory from static files..."
mkdir -p /app/build/static/{css,js,media}
cp /app/static-index.html /app/build/index.html
cp /app/static-manifest.json /app/build/manifest.json  
cp /app/static-asset-manifest.json /app/build/asset-manifest.json
echo 'body{font-family:serif}' > /app/build/static/css/main.css
echo 'console.log("Acta Diurna")' > /app/build/static/js/main.js
echo "Build directory created successfully"
ls -la /app/build/