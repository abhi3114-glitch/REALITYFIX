/**
 * Content Script - FIXED VERSION with better error handling
 * Extracts page content for analysis
 */

// Log when content script loads
console.log('RealityFix: Content script loaded on', window.location.href);

// Extract page text (first 5000 characters)
function extractPageText() {
  try {
    // Try multiple methods to get text
    let text = '';
    
    // Method 1: innerText (preferred, excludes hidden elements)
    if (document.body.innerText) {
      text = document.body.innerText;
    }
    // Method 2: textContent (fallback)
    else if (document.body.textContent) {
      text = document.body.textContent;
    }
    
    // Clean up whitespace
    text = text.replace(/\s+/g, ' ').trim();
    
    // Limit length
    const result = text.substring(0, 5000);
    
    console.log('RealityFix: Extracted', result.length, 'characters of text');
    return result;
    
  } catch (error) {
    console.error('RealityFix: Error extracting text:', error);
    return '';
  }
}

// Extract all image URLs from the page
function extractImages() {
  try {
    const images = Array.from(document.querySelectorAll('img'));
    const imageUrls = images
      .map(img => img.src)
      .filter(src => src && (src.startsWith('http://') || src.startsWith('https://')))
      .filter(src => !src.includes('data:image')) // Skip data URLs
      .slice(0, 10); // Limit to first 10 images
    
    console.log('RealityFix: Extracted', imageUrls.length, 'images');
    return imageUrls;
    
  } catch (error) {
    console.error('RealityFix: Error extracting images:', error);
    return [];
  }
}

// Extract video information
function extractVideos() {
  try {
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
    
    console.log('RealityFix: Extracted', videos.length, 'videos');
    return videos.slice(0, 5);
    
  } catch (error) {
    console.error('RealityFix: Error extracting videos:', error);
    return [];
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('RealityFix: Received message:', request.action);
  
  if (request.action === 'extractContent') {
    try {
      const pageData = {
        url: window.location.href,
        title: document.title,
        text: extractPageText(),
        images: extractImages(),
        videos: extractVideos(),
        timestamp: new Date().toISOString()
      };
      
      console.log('RealityFix: Extracted page data:', {
        url: pageData.url,
        title: pageData.title,
        textLength: pageData.text.length,
        imageCount: pageData.images.length,
        videoCount: pageData.videos.length
      });
      
      sendResponse({ success: true, data: pageData });
      
    } catch (error) {
      console.error('RealityFix: Error in extractContent:', error);
      sendResponse({ 
        success: false, 
        error: error.message 
      });
    }
  }
  
  return true; // Keep message channel open for async response
});

// Log successful initialization
console.log('RealityFix: Content script ready');