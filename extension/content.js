/**
 * Content Script - Extracts page content for analysis
 * Runs on every webpage to collect text, images, and video data
 */

// Extract page text (first 5000 characters)
function extractPageText() {
  const bodyText = document.body.innerText || document.body.textContent || '';
  return bodyText.substring(0, 5000).trim();
}

// Extract all image URLs from the page
function extractImages() {
  const images = Array.from(document.querySelectorAll('img'));
  return images
    .map(img => img.src)
    .filter(src => src && (src.startsWith('http://') || src.startsWith('https://')))
    .slice(0, 10); // Limit to first 10 images
}

// Extract video information (YouTube focus)
function extractVideos() {
  const videos = [];
  
  // Check if it's a YouTube page
  if (window.location.hostname.includes('youtube.com')) {
    const title = document.querySelector('h1.title yt-formatted-string, h1.ytd-video-primary-info-renderer')?.textContent?.trim();
    const videoId = new URLSearchParams(window.location.search).get('v');
    
    if (title && videoId) {
      videos.push({
        title: title,
        url: window.location.href,
        videoId: videoId,
        platform: 'youtube'
      });
    }
  }
  
  // Extract other video elements
  const videoElements = Array.from(document.querySelectorAll('video'));
  videoElements.forEach(video => {
    if (video.src) {
      videos.push({
        title: video.title || 'Video',
        url: video.src,
        platform: 'other'
      });
    }
  });
  
  return videos.slice(0, 5);
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractContent') {
    const pageData = {
      url: window.location.href,
      title: document.title,
      text: extractPageText(),
      images: extractImages(),
      videos: extractVideos(),
      timestamp: new Date().toISOString()
    };
    
    sendResponse({ success: true, data: pageData });
  }
  return true; // Keep message channel open for async response
});

// Auto-analyze on page load (optional)
window.addEventListener('load', () => {
  console.log('RealityFix: Content script loaded');
});