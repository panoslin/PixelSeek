#!/bin/bash

# Exit on error
set -e

echo "Building PixelSeek Chrome Extension..."

# Build the Angular app
echo "Building Angular components..."
ng build

# Create directories in the dist folder
echo "Creating necessary directories..."
mkdir -p dist/content
mkdir -p dist/background

# Compile the TypeScript content script
echo "Compiling content scripts..."
npx tsc -p tsconfig.content.json

# Copy the manifest
echo "Copying manifest..."
cp manifest.json dist/

# Copy the background script
echo "Copying background script..."
cp src/background/background.js dist/background/

# Success message
echo "Build completed successfully! The extension is in the 'dist' folder." 