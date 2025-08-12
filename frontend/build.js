#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('Starting build process...');

// Define build directory (relative to frontend directory)
const buildDir = path.join('..', 'build');
const staticDir = path.join(buildDir, 'static');

try {
  // Clean existing build directory
  console.log('Cleaning build directory...');
  if (fs.existsSync(buildDir)) {
    fs.rmSync(buildDir, { recursive: true, force: true });
  }

  // Create directory structure
  console.log('Creating directory structure...');
  fs.mkdirSync(path.join(staticDir, 'js'), { recursive: true });
  fs.mkdirSync(path.join(staticDir, 'css'), { recursive: true });
  fs.mkdirSync(path.join(staticDir, 'media'), { recursive: true });

  // Create index.html
  console.log('Creating index.html...');
  const indexHtml = `<!DOCTYPE html>
<html>
<head>
    <title>Flask App Redirect</title>
    <meta http-equiv="refresh" content="0; url=/">
</head>
<body>
    <p>Redirecting to Flask app...</p>
    <script>window.location.href = '/';</script>
</body>
</html>`;
  fs.writeFileSync(path.join(buildDir, 'index.html'), indexHtml);

  // Create main.css
  console.log('Creating main.css...');
  const mainCss = '/* Placeholder CSS file for deployment compatibility */\nbody { font-family: Arial, sans-serif; }';
  fs.writeFileSync(path.join(staticDir, 'css', 'main.css'), mainCss);

  // Create main.js
  console.log('Creating main.js...');
  const mainJs = '// Placeholder JS file for deployment compatibility\nconsole.log("Flask app loaded");';
  fs.writeFileSync(path.join(staticDir, 'js', 'main.js'), mainJs);

  // Create manifest.json
  console.log('Creating manifest.json...');
  const manifest = {
    "short_name": "Acta Diurna",
    "name": "Acta Diurna - Personal Daily Chronicle", 
    "start_url": ".",
    "display": "standalone",
    "theme_color": "#f59e0b",
    "background_color": "#ffffff"
  };
  fs.writeFileSync(path.join(buildDir, 'manifest.json'), JSON.stringify(manifest, null, 2));

  // Create asset-manifest.json
  console.log('Creating asset-manifest.json...');
  const assetManifest = {
    "files": {
      "main.css": "/static/css/main.css",
      "main.js": "/static/js/main.js", 
      "index.html": "/index.html"
    },
    "entrypoints": [
      "static/css/main.css",
      "static/js/main.js"
    ]
  };
  fs.writeFileSync(path.join(buildDir, 'asset-manifest.json'), JSON.stringify(assetManifest, null, 2));

  // Verify all files were created
  console.log('Verifying files...');
  const requiredFiles = [
    path.join(buildDir, 'index.html'),
    path.join(buildDir, 'asset-manifest.json'),
    path.join(buildDir, 'manifest.json'),
    path.join(staticDir, 'css', 'main.css'),
    path.join(staticDir, 'js', 'main.js')
  ];

  for (const file of requiredFiles) {
    if (!fs.existsSync(file)) {
      throw new Error(`Required file missing: ${file}`);
    }
  }

  console.log('✅ Build completed successfully - all required files created');
  console.log('📁 Output directory: /app/build');

} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}