#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('=== Starting Acta Diurna Build Process ===');

// Define build directory (relative to frontend directory)
const buildDir = path.resolve(__dirname, '..', 'build');
const staticDir = path.join(buildDir, 'static');

try {
  console.log(`Build directory: ${buildDir}`);
  
  // Clean existing build directory
  console.log('Cleaning build directory...');
  if (fs.existsSync(buildDir)) {
    fs.rmSync(buildDir, { recursive: true, force: true });
    console.log('✅ Old build directory removed');
  }

  // Create directory structure
  console.log('Creating directory structure...');
  fs.mkdirSync(buildDir, { recursive: true });
  fs.mkdirSync(path.join(staticDir, 'js'), { recursive: true });
  fs.mkdirSync(path.join(staticDir, 'css'), { recursive: true });
  fs.mkdirSync(path.join(staticDir, 'media'), { recursive: true });
  console.log('✅ Directory structure created');

  // Create index.html
  console.log('Creating index.html...');
  const indexHtml = `<!DOCTYPE html>
<html>
<head>
    <title>Acta Diurna - Flask App</title>
    <meta http-equiv="refresh" content="0; url=/">
    <meta name="description" content="Acta Diurna - Your Personal Daily Chronicle">
</head>
<body>
    <p>Redirecting to Acta Diurna...</p>
    <script>
        setTimeout(function() {
            window.location.href = '/';
        }, 100);
    </script>
</body>
</html>`;
  fs.writeFileSync(path.join(buildDir, 'index.html'), indexHtml);
  console.log('✅ index.html created');

  // Create main.css
  console.log('Creating main.css...');
  const mainCss = `/* Acta Diurna Build CSS - Deployment Compatibility */
body { 
  font-family: Georgia, serif; 
  margin: 0; 
  padding: 0; 
}
.build-notice { 
  display: none; 
}`;
  fs.writeFileSync(path.join(staticDir, 'css', 'main.css'), mainCss);
  console.log('✅ main.css created');

  // Create main.js
  console.log('Creating main.js...');
  const mainJs = `// Acta Diurna Build JS - Deployment Compatibility
console.log('Acta Diurna Flask application loaded successfully');
document.addEventListener('DOMContentLoaded', function() {
  console.log('Build system: Emergent deployment ready');
});`;
  fs.writeFileSync(path.join(staticDir, 'js', 'main.js'), mainJs);
  console.log('✅ main.js created');

  // Create manifest.json
  console.log('Creating manifest.json...');
  const manifest = {
    "short_name": "Acta Diurna",
    "name": "Acta Diurna - Your Personal Daily Chronicle", 
    "start_url": "/",
    "display": "standalone",
    "theme_color": "#f59e0b",
    "background_color": "#ffffff",
    "description": "Share stories and read the latest news from your friends",
    "icons": []
  };
  fs.writeFileSync(path.join(buildDir, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log('✅ manifest.json created');

  // Create asset-manifest.json
  console.log('Creating asset-manifest.json...');
  const assetManifest = {
    "files": {
      "main.css": "/static/css/main.css",
      "main.js": "/static/js/main.js", 
      "index.html": "/index.html",
      "manifest.json": "/manifest.json"
    },
    "entrypoints": [
      "static/css/main.css",
      "static/js/main.js"
    ]
  };
  fs.writeFileSync(path.join(buildDir, 'asset-manifest.json'), JSON.stringify(assetManifest, null, 2));
  console.log('✅ asset-manifest.json created');

  // Verify all files were created
  console.log('Verifying build output...');
  const requiredFiles = [
    path.join(buildDir, 'index.html'),
    path.join(buildDir, 'asset-manifest.json'),
    path.join(buildDir, 'manifest.json'),
    path.join(staticDir, 'css', 'main.css'),
    path.join(staticDir, 'js', 'main.js')
  ];

  let allFilesExist = true;
  for (const file of requiredFiles) {
    if (!fs.existsSync(file)) {
      console.error(`❌ Required file missing: ${file}`);
      allFilesExist = false;
    } else {
      const stats = fs.statSync(file);
      console.log(`✅ ${path.relative(buildDir, file)} (${stats.size} bytes)`);
    }
  }

  if (!allFilesExist) {
    throw new Error('Build verification failed - missing required files');
  }

  // Final directory listing
  console.log('\n=== Build Output Structure ===');
  function listDirectory(dir, prefix = '') {
    const items = fs.readdirSync(dir, { withFileTypes: true });
    items.forEach(item => {
      if (item.isDirectory()) {
        console.log(`${prefix}📁 ${item.name}/`);
        listDirectory(path.join(dir, item.name), prefix + '  ');
      } else {
        const stats = fs.statSync(path.join(dir, item.name));
        console.log(`${prefix}📄 ${item.name} (${stats.size} bytes)`);
      }
    });
  }
  listDirectory(buildDir);

  console.log('\n🎉 BUILD COMPLETED SUCCESSFULLY');
  console.log(`📁 Output directory: ${buildDir}`);
  console.log('🚀 Ready for Emergent deployment!');

} catch (error) {
  console.error('\n❌ BUILD FAILED');
  console.error('Error:', error.message);
  console.error('Stack:', error.stack);
  process.exit(1);
}