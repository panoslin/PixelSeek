/// <reference types="chrome"/>
/**
 * Content script for detecting video elements on the page
 */

// Function to get video element details
function getVideoDetails(video: HTMLVideoElement) {
  const url = video.currentSrc || video.src;
  if (!url) return null;
  
  return {
    url,
    duration: video.duration || 0,
    dimensions: {
      width: video.videoWidth || 0,
      height: video.videoHeight || 0
    }
  };
}

// Function to check all video elements on the page
function checkVideosOnPage() {
  const videos = document.querySelectorAll('video');
  
  videos.forEach(video => {
    const videoElement = video as HTMLVideoElement;
    const details = getVideoDetails(videoElement);
    if (details?.url) {
      // Send the video details to the background script
      chrome.runtime.sendMessage({
        action: 'video_detected_in_page',
        ...details
      });
    }
    
    // Add listeners for videos that load their source later
    if (!videoElement.hasAttribute('data-pixelseek-listener')) {
      videoElement.setAttribute('data-pixelseek-listener', 'true');
      
      videoElement.addEventListener('loadedmetadata', () => {
        const updatedDetails = getVideoDetails(videoElement);
        if (updatedDetails?.url) {
          chrome.runtime.sendMessage({
            action: 'video_detected_in_page',
            ...updatedDetails
          });
        }
      });
    }
  });
  
  // Also check for source elements within video tags
  const sources = document.querySelectorAll('video source');
  sources.forEach(source => {
    const sourceElement = source as HTMLSourceElement;
    const url = sourceElement.src;
    if (url) {
      chrome.runtime.sendMessage({
        action: 'video_detected_in_page',
        url,
        duration: 0,
        dimensions: { width: 0, height: 0 }
      });
    }
  });
}

// Initial check when content script loads
checkVideosOnPage();

// Set up mutation observer to detect dynamically added videos
const observer = new MutationObserver(mutations => {
  let shouldCheck = false;
  
  mutations.forEach(mutation => {
    // Check if any video elements were added
    if (mutation.addedNodes.length) {
      Array.from(mutation.addedNodes).forEach(node => {
        if (node instanceof HTMLElement) {
          if (node.tagName === 'VIDEO' || node.querySelector('video')) {
            shouldCheck = true;
          }
        }
      });
    }
    
    // Check if any attributes were changed on video elements
    if (mutation.type === 'attributes' && mutation.target instanceof HTMLVideoElement) {
      if (mutation.attributeName === 'src') {
        shouldCheck = true;
      }
    }
  });
  
  if (shouldCheck) {
    checkVideosOnPage();
  }
});

// Start observing the document with the configured parameters
observer.observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ['src']
});

// Re-check periodically for videos that might be added by JavaScript
setInterval(checkVideosOnPage, 5000);

// Listen for messages from the extension
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'force_check_videos') {
    checkVideosOnPage();
    sendResponse({ status: 'checked' });
  }
  return true;
}); 