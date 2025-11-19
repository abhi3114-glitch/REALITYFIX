/**
 * Background Service Worker - FIXED VERSION with URL passing
 * Handles API communication and passes URL for domain trust scoring
 */

const API_BASE_URL = 'http://localhost:8000';

console.log('RealityFix: Background service worker started');

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('RealityFix Background: Received message:', request.action);
  
  if (request.action === 'analyzeContent') {
    analyzeContent(request.data)
      .then(result => {
        console.log('RealityFix Background: Analysis complete');
        sendResponse({ success: true, result });
      })
      .catch(error => {
        console.error('RealityFix Background: Analysis failed:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true; // Keep message channel open
  }
  
  if (request.action === 'updateBadge') {
    updateBadge(request.score, sender.tab?.id);
    sendResponse({ success: true });
  }
  
  return true;
});

// Analyze content by calling backend API
async function analyzeContent(pageData) {
  console.log('RealityFix Background: Starting analysis...');
  console.log('Page URL:', pageData.url);
  
  try {
    // Validate input
    if (!pageData.text || pageData.text.length < 10) {
      throw new Error('Not enough text content to analyze');
    }
    
    // Analyze text WITH URL for domain trust scoring
    console.log('RealityFix Background: Analyzing text with domain trust...');
    const textAnalysis = await analyzeText(pageData.text, pageData.url);
    
    // Analyze images (first image only for MVP)
    let imageAnalysis = null;
    if (pageData.images && pageData.images.length > 0) {
      console.log('RealityFix Background: Analyzing image...');
      try {
        imageAnalysis = await analyzeImage(pageData.images[0]);
      } catch (imgError) {
        console.warn('RealityFix Background: Image analysis failed:', imgError.message);
        // Continue without image analysis
      }
    }
    
    // Combine results
    const combinedScore = calculateCombinedScore(textAnalysis, imageAnalysis);
    
    console.log('RealityFix Background: Combined score:', combinedScore);
    
    return {
      score: combinedScore.score,
      label: combinedScore.label,
      confidence: combinedScore.confidence,
      textAnalysis,
      imageAnalysis,
      evidence: textAnalysis.evidence || [],
      reportId: textAnalysis.report_id,
      sourceUrl: pageData.url
    };
    
  } catch (error) {
    console.error('RealityFix Background: Analysis error:', error);
    throw error;
  }
}

// Analyze text content with URL for domain trust
async function analyzeText(text, url) {
  console.log('RealityFix Background: Sending text to API with URL...');
  
  try {
    // Include URL in request for domain trust scoring
    const requestBody = {
      text: text,
      url: url  // Add URL to request
    };
    
    const response = await fetch(`${API_BASE_URL}/analyze/text`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    console.log('RealityFix Background: API response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('RealityFix Background: API error:', errorText);
      throw new Error(`Text analysis failed: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('RealityFix Background: Text analysis result:', result);
    return result;
    
  } catch (error) {
    console.error('RealityFix Background: Text analysis error:', error);
    
    // Provide more helpful error message
    if (error.message.includes('Failed to fetch')) {
      throw new Error('Cannot connect to backend. Please start the server with: python backend/app.py');
    }
    
    throw error;
  }
}

// Analyze image
async function analyzeImage(imageUrl) {
  console.log('RealityFix Background: Sending image to API:', imageUrl);
  
  try {
    const response = await fetch(`${API_BASE_URL}/analyze/image`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ image_url: imageUrl })
    });
    
    console.log('RealityFix Background: Image API response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('RealityFix Background: Image API error:', errorText);
      throw new Error(`Image analysis failed: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('RealityFix Background: Image analysis result:', result);
    return result;
    
  } catch (error) {
    console.error('RealityFix Background: Image analysis error:', error);
    throw error;
  }
}

// Calculate combined score from multiple analyses
function calculateCombinedScore(textAnalysis, imageAnalysis) {
  let totalScore = 0;
  let count = 0;
  
  if (textAnalysis && typeof textAnalysis.score === 'number') {
    totalScore += textAnalysis.score;
    count++;
  }
  
  if (imageAnalysis && typeof imageAnalysis.score === 'number') {
    totalScore += imageAnalysis.score;
    count++;
  }
  
  const avgScore = count > 0 ? totalScore / count : 0.5;
  
  // Determine label
  let label = 'suspicious';
  if (avgScore >= 0.7) {
    label = 'trustworthy';
  } else if (avgScore < 0.4) {
    label = 'misinformation';
  }
  
  const result = {
    score: Math.round(avgScore * 100),
    label,
    confidence: count > 0 ? Math.min(0.9, 0.6 + (count * 0.15)) : 0.5
  };
  
  console.log('RealityFix Background: Combined score calculated:', result);
  return result;
}

// Update extension badge with trust score
function updateBadge(score, tabId) {
  if (!tabId) {
    console.warn('RealityFix Background: No tab ID for badge update');
    return;
  }
  
  let color = '#FFA500'; // Orange for suspicious
  if (score >= 70) {
    color = '#4CAF50'; // Green for trustworthy
  } else if (score < 40) {
    color = '#F44336'; // Red for misinformation
  }
  
  console.log('RealityFix Background: Updating badge -', score, color);
  
  chrome.action.setBadgeText({ text: score.toString(), tabId });
  chrome.action.setBadgeBackgroundColor({ color, tabId });
}

// Installation handler
chrome.runtime.onInstalled.addListener(() => {
  console.log('RealityFix extension installed');
});

// Log that service worker is ready
console.log('RealityFix: Background service worker ready');