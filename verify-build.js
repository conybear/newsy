#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('=== Build Verification Script ===');

const buildDir = path.join(__dirname, 'build');
const requiredFiles = [
  'index.html',
  'asset-manifest.json', 
  'manifest.json',
  'static/css/main.css',
  'static/js/main.js'
];

console.log(`Checking build directory: ${buildDir}`);

if (!fs.existsSync(buildDir)) {
  console.error('❌ Build directory does not exist');
  console.log('Running build process...');
  
  const { execSync } = require('child_process');
  try {
    execSync('cd frontend && yarn build', { stdio: 'inherit' });
    console.log('✅ Build process completed');
  } catch (error) {
    console.error('❌ Build process failed:', error.message);
    process.exit(1);
  }
}

let allFilesExist = true;
console.log('\nVerifying required files:');

for (const file of requiredFiles) {
  const filePath = path.join(buildDir, file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`✅ ${file} (${stats.size} bytes)`);
  } else {
    console.error(`❌ Missing: ${file}`);
    allFilesExist = false;
  }
}

if (allFilesExist) {
  console.log('\n🎉 Build verification PASSED - ready for deployment!');
  process.exit(0);
} else {
  console.error('\n❌ Build verification FAILED - missing required files');
  process.exit(1);
}