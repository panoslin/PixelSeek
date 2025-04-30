/**
 * Background service worker for intercepting video URLs
 */

// In-memory store of detected video URLs
const videoUrlStore = new Map();

// Media types we're interested in capturing
const MEDIA_TYPES = ['video/mp4', 'video/webm', 'application/x-mpegURL', 'application/vnd.apple.mpegurl'];
const VIDEO_EXTENSIONS = ['.mp4', '.webm', '.m3u8', '.ts'];

// Listen for all web requests that might include video content
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    // Skip requests from our extension
    if (details.initiator && details.initiator.startsWith('chrome-extension://')) {
      return;
    }

    const url = details.url.toLowerCase();
    
    // Check if URL has a video file extension
    const hasVideoExtension = VIDEO_EXTENSIONS.some(ext => url.endsWith(ext));
    
    if (hasVideoExtension || details.type === 'media') {
      // Store video URL with timestamp and tab info
      const videoInfo = {
        url: details.url,
        tabId: details.tabId,
        timestamp: Date.now(),
        type: details.type,
        filename: getFilenameFromUrl(details.url)
      };
      
      // Use URL as key to avoid duplicates
      videoUrlStore.set(details.url, videoInfo);
      
      // Notify all UI components about the new video
      notifyVideoDetected(videoInfo);
    }
  },
  { urls: ["<all_urls>"] },
  ["requestBody"]
);

// Also listen for video content loaded in the page 
// (will be communicated from content scripts)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'video_detected_in_page') {
    // Add detected video to our store
    const videoInfo = {
      url: message.url,
      tabId: sender.tab?.id,
      timestamp: Date.now(),
      type: 'content_script',
      filename: getFilenameFromUrl(message.url),
      duration: message.duration,
      dimensions: message.dimensions
    };
    
    videoUrlStore.set(message.url, videoInfo);
    
    // Notify UI about the video
    notifyVideoDetected(videoInfo);
    sendResponse({ success: true });
  } else if (message.action === 'get_videos') {
    // Return all stored videos for sidebar UI
    sendResponse({ videos: Array.from(videoUrlStore.values()) });
  } else if (message.action === 'download_video') {
    // Initiate download of a video
    chrome.downloads.download({
      url: message.url,
      filename: message.filename || getFilenameFromUrl(message.url),
      saveAs: true
    }).then(downloadId => {
      sendResponse({ success: true, downloadId });
    }).catch(error => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // Keep the message channel open for the async response
  }
});

// Show side panel when the extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ tabId: tab.id });
});

// Utility function to extract filename from URL
function getFilenameFromUrl(url) {
  try {
    const urlObj = new URL(url);
    const pathname = urlObj.pathname;
    let filename = pathname.split('/').pop() || 'video';
    
    // Clean the filename
    filename = filename.split('?')[0];
    
    // Add extension if missing
    if (!VIDEO_EXTENSIONS.some(ext => filename.endsWith(ext))) {
      filename += '.mp4';
    }
    
    return filename;
  } catch (e) {
    return 'video.mp4';
  }
}

// Notify UI components about newly detected video
function notifyVideoDetected(videoInfo) {
  chrome.runtime.sendMessage({
    action: 'video_detected',
    video: videoInfo
  }).catch(() => {
    // UI might not be open, which is fine
  });
}

// When extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  console.log('PixelSeek extension installed or updated');
  videoUrlStore.clear();
}); 