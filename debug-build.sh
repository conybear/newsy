#!/bin/bash
echo "=== BUILD DEBUG INFORMATION ==="
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la
echo ""
echo "Frontend directory:"
ls -la frontend/ 2>/dev/null || echo "Frontend directory not found"
echo ""
echo "Build directory status:"
if [ -d "build" ]; then
    echo "✅ Build directory exists:"
    ls -la build/
    echo ""
    echo "Build directory contents (recursive):"
    find build -type f | sort
else
    echo "❌ Build directory does not exist"
fi
echo ""
echo "Package.json files:"
find . -name "package.json" -exec echo "Found: {}" \; -exec cat {} \;
echo ""
echo "Node and Yarn versions:"
node --version 2>/dev/null || echo "Node not available"
yarn --version 2>/dev/null || echo "Yarn not available"
echo "=== END DEBUG INFO ==="