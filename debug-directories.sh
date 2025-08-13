#!/bin/bash
echo "=== DIRECTORY DEBUG SCRIPT ==="
echo "Current directory: $(pwd)"
echo ""
echo "All directories in /app:"
find /app -type d | sort
echo ""
echo "Looking for build-related directories:"
find /app -name "*build*" -o -name "dist" -o -name "assets" -o -name "static" -o -name "public" -o -name "www" | sort
echo ""
echo "Files in each directory:"
for dir in build dist assets static public www; do
  if [ -d "/app/$dir" ]; then
    echo "=== /app/$dir ==="
    ls -la "/app/$dir"
    echo ""
  fi
done