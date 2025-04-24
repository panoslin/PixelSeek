// Chrome extension background script
console.log('PixelSeek extension background script loaded');

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('PixelSeek extension has been installed');
  } else if (details.reason === 'update') {
    console.log('PixelSeek extension has been updated');
  }
});

// Example: Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Received message:', message);
  
  // Send a response back
  sendResponse({ status: 'Message received by background script' });
  
  // Return true to indicate you wish to send a response asynchronously
  return true;
}); 