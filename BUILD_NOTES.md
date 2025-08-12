# Build Process Documentation

## Emergent/Kaniko Deployment Requirements

This application is configured for deployment on Emergent platform which uses Kaniko for containerization. The build process must create specific files and directories in exact locations.

## Critical Requirements

### Build Output Location
- **MUST** create `/app/build` directory (not `/app/frontend/build`)
- This path is hardcoded in Emergent's deployment system

### Required Files
The build process must create these files:
- `build/index.html`
- `build/asset-manifest.json`
- `build/manifest.json`
- `build/static/css/main.css`
- `build/static/js/main.js`

### Required Directory Structure
```
/app/build/
├── index.html
├── asset-manifest.json
├── manifest.json
└── static/
    ├── css/
    │   └── main.css
    ├── js/
    │   └── main.js
    └── media/
```

## Build Commands

### Development Build
```bash
cd /app
./build.sh
```

### Production Build (as used by Emergent)
```bash
cd /app/frontend
yarn build
```

### Test Build Process
```bash
cd /app
./test-build.sh
```

## Build Script Features

- **Error Handling**: Uses `set -e` to fail fast on any error
- **Verification**: Checks all required files are created
- **Clean Build**: Removes old build directory before creating new one
- **Logging**: Detailed output for debugging deployment issues

## Path Synchronization

All build paths are consistent:
- Frontend package.json points to `/app/build`
- Flask app serves from root `/app`
- Emergent deployment expects `/app/build`

No hardcoded alternative paths like `/app/frontend/build` are used anywhere.

## Deployment Notes

When Emergent runs the build:
1. Installs frontend dependencies (`yarn install`)
2. Runs build command (`yarn build`)  
3. Expects to find `/app/build` directory
4. Copies build files to container
5. Starts Flask app with Gunicorn via `Procfile`

The build must succeed without errors or deployment will fail with:
```
failed to get fileinfo for /kaniko/0/app/build: no such file or directory
```