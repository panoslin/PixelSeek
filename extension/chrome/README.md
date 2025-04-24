# PixelSeek Chrome Extension

A Chrome extension for PixelSeek built with Angular 17 using standalone components and TypeScript.

## Development Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Start development server:
   ```
   npm start
   ```

3. Build the extension:
   ```
   npm run build:extension
   ```

## Loading the Extension in Chrome

1. Build the extension using `npm run build:extension`
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in the top-right corner)
4. Click "Load unpacked" and select the `dist` folder
5. The extension should now appear in your browser toolbar

## Technical Details

This extension uses Angular 17's standalone components architecture, which provides several benefits:
- No NgModules required, reducing boilerplate code
- Simpler component management and dependency injection
- Better tree-shaking capabilities for smaller bundle sizes

## Note About Icons

Before publishing, you need to replace the placeholder icons in the `src/assets` folder with your own icons in the following sizes:
- 16x16 (icon16.png)
- 48x48 (icon48.png)
- 128x128 (icon128.png)

## Features

- Simple "Hello World" demonstration
- Background script for Chrome extension functionality
- Angular-based popup UI with standalone components 