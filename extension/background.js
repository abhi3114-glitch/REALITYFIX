/**
 * Background Service Worker - Handles API communication
 * Manages requests to backend and badge updates
 */

const API_BASE_URL = 'http://localhost:8000';

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeContent') {
    analyzeContent(request.data)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep message channel open
  }
  
  if (request.action === 'updateBadge') {
    updateBadge(request.score, sender.tab?.id);
    sendResponse({ success: true });
  }
});

// Analyze content by calling backend API
async function analyzeContent(pageData) {
  try {
    // Analyze text
    const textAnalysis = await analyzeText(pageData.text);
    
    // Analyze images (first image only for MVP)
    let imageAnalysis = null;
    if (pageData.images && pageData.images.length > 0) {
      imageAnalysis = await analyzeImage(pageData.images[0]);
    }
    
    // Combine results
    const combinedScore = calculateCombinedScore(textAnalysis, imageAnalysis);
    
    return {
      score: combinedScore.score,
      label: combinedScore.label,
      confidence: combinedScore.confidence,
      textAnalysis,
      imageAnalysis,
      evidence: textAnalysis.evidence || [],
      reportId: textAnalysis.report_id
    };
  } catch (error) {
    console.error('Analysis error:', error);
    throw error;
  }
}

// Analyze text content
async function analyzeText(text) {
  const response = await fetch(`${API_BASE_URL}/analyze/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  
  if (!response.ok) {
    throw new Error(`Text analysis failed: ${response.statusText}`);
  }
  
  return await response.json();
}

// Analyze image
async function analyzeImage(imageUrl) {
  const response = await fetch(`${API_BASE_URL}/analyze/image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_url: imageUrl })
  });
  
  if (!response.ok) {
    throw new Error(`Image analysis failed: ${response.statusText}`);
  }
  
  return await response.json();
}

// Calculate combined score from multiple analyses
function calculateCombinedScore(textAnalysis, imageAnalysis) {
  let totalScore = 0;
  let count = 0;
  
  if (textAnalysis) {
    totalScore += textAnalysis.score;
    count++;
  }
  
  if (imageAnalysis) {
    totalScore += imageAnalysis.score;
    count++;
  }
  
  const avgScore = count > 0 ? totalScore / count : 0.5;
  
  // Determine label
  let label = 'suspicious';
  if (avgScore >= 0.7) label = 'trustworthy';
  else if (avgScore < 0.4) label = 'misinformation';
  
  return {
    score: Math.round(avgScore * 100),
    label,
    confidence: count > 0 ? Math.min(0.9, 0.6 + (count * 0.15)) : 0.5
  };
}

// Update extension badge with trust score
function updateBadge(score, tabId) {
  if (!tabId) return;
  
  let color = '#FFA500'; // Orange for suspicious
  if (score >= 70) color = '#4CAF50'; // Green for trustworthy
  else if (score < 40) color = '#F44336'; // Red for misinformation
  
  chrome.action.setBadgeText({ text: score.toString(), tabId });
  chrome.action.setBadgeBackgroundColor({ color, tabId });
}

// Installation handler
chrome.runtime.onInstalled.addListener(() => {
  console.log('RealityFix extension installed');
});