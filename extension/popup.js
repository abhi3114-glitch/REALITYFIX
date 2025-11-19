/**
 * RealityFix Popup Script - Complete Fixed Version
 * Handles UI interactions and displays analysis results
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const DEBUG_MODE = true; // Set to false in production

// DOM Elements
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const errorMessageEl = document.getElementById('errorMessage');
const resultsEl = document.getElementById('results');
const initialStateEl = document.getElementById('initialState');
const debugInfoEl = document.getElementById('debugInfo');
const debugContentEl = document.getElementById('debugContent');

const scoreValueEl = document.getElementById('scoreValue');
const scoreCircleEl = document.getElementById('scoreCircle');
const statusBadgeEl = document.getElementById('statusBadge');
const confidenceEl = document.getElementById('confidence');
const summaryTextEl = document.getElementById('summaryText');
const evidenceListEl = document.getElementById('evidenceList');

const fullReportBtn = document.getElementById('fullReportBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const firstAnalyzeBtn = document.getElementById('firstAnalyzeBtn');
const retryBtn = document.getElementById('retryBtn');
const debugBtn = document.getElementById('debugBtn');
const closeDebugBtn = document.getElementById('closeDebugBtn');

const backendStatusEl = document.getElementById('backendStatus');
const backendStatusTextEl = document.getElementById('backendStatusText');

// State
let currentReportId = null;
let debugLogs = [];

// Utility: Log with timestamp
function log(message, data = null) {
  const timestamp = new Date().toISOString();
  const logEntry = { timestamp, message, data };
  debugLogs.push(logEntry);
  
  if (DEBUG_MODE) {
    console.log(`[${timestamp}] ${message}`, data || '');
  }
}

// Utility: Add to debug info
function addDebugInfo(key, value) {
  const debugItem = document.createElement('div');
  debugItem.className = 'debug-item';
  debugItem.innerHTML = `<strong>${key}:</strong> ${JSON.stringify(value, null, 2)}`;
  debugContentEl.appendChild(debugItem);
}

// Initialize popup
document.addEventListener('DOMContentLoaded', () => {
  log('Popup initialized');
  
  // Set up event listeners
  analyzeBtn?.addEventListener('click', analyzePage);
  firstAnalyzeBtn?.addEventListener('click', analyzePage);
  retryBtn?.addEventListener('click', analyzePage);
  fullReportBtn?.addEventListener('click', openFullReport);
  debugBtn?.addEventListener('click', showDebugInfo);
  closeDebugBtn?.addEventListener('click', hideDebugInfo);
  
  // Test backend connection
  testBackendConnection();
  
  // Load cached results
  loadCachedResults();
});

// Test backend connection
async function testBackendConnection() {
  log('Testing backend connection...');
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      log('Backend connected', data);
      updateBackendStatus(true, 'Backend Online');
      return true;
    } else {
      log('Backend returned error', response.status);
      updateBackendStatus(false, 'Backend Error');
      return false;
    }
  } catch (error) {
    log('Backend connection failed', error.message);
    
    if (error.name === 'AbortError') {
      updateBackendStatus(false, 'Backend Timeout');
    } else {
      updateBackendStatus(false, 'Backend Offline');
    }
    
    return false;
  }
}

// Update backend status indicator
function updateBackendStatus(isOnline, statusText) {
  if (backendStatusEl && backendStatusTextEl) {
    backendStatusEl.style.color = isOnline ? '#4CAF50' : '#F44336';
    backendStatusTextEl.textContent = statusText;
  }
}

// Analyze current page
async function analyzePage() {
  log('Starting page analysis...');
  debugLogs = []; // Reset debug logs
  
  try {
    showLoading();
    hideError();
    hideDebugInfo();
    
    // Step 1: Get current tab
    log('Getting current tab...');
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tabs || tabs.length === 0) {
      throw new Error('No active tab found. Please try again.');
    }
    
    const tab = tabs[0];
    log('Current tab', { id: tab.id, url: tab.url, title: tab.title });
    
    // Step 2: Check if URL is accessible
    if (!tab.url) {
      throw new Error('Cannot access this page. Try a different tab.');
    }
    
    if (tab.url.startsWith('chrome://') || 
        tab.url.startsWith('chrome-extension://') ||
        tab.url.startsWith('edge://') ||
        tab.url.startsWith('about:')) {
      throw new Error('Cannot analyze browser internal pages. Please navigate to a regular website (like news.ycombinator.com, bbc.com, or any news site).');
    }
    
    // Step 3: Extract content from page
    log('Extracting content from page...');
    let response;
    
    try {
      response = await chrome.tabs.sendMessage(tab.id, { action: 'extractContent' });
      log('Content extraction response', response);
    } catch (msgError) {
      log('Content script error', msgError);
      
      // Try to inject content script if it's not loaded
      try {
        log('Attempting to inject content script...');
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content.js']
        });
        
        // Wait a bit for script to initialize
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Try again
        response = await chrome.tabs.sendMessage(tab.id, { action: 'extractContent' });
        log('Content extraction after injection', response);
      } catch (injectError) {
        log('Content script injection failed', injectError);
        throw new Error('Failed to extract page content. Please refresh the page and try again.');
      }
    }
    
    // Step 4: Validate extracted data
    if (!response || !response.success) {
      throw new Error('Failed to extract page content. Please refresh the page.');
    }
    
    if (!response.data) {
      throw new Error('No data extracted from page.');
    }
    
    log('Extracted data', {
      textLength: response.data.text?.length || 0,
      imageCount: response.data.images?.length || 0,
      videoCount: response.data.videos?.length || 0
    });
    
    // Check if there's enough content
    if (!response.data.text || response.data.text.trim().length < 50) {
      throw new Error('Not enough text content on this page. Try a page with more text (at least 50 characters).');
    }
    
    // Step 5: Send to background for analysis
    log('Sending to background script...');
    const analysisResponse = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        {
          action: 'analyzeContent',
          data: response.data
        },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else {
            resolve(response);
          }
        }
      );
    });
    
    log('Analysis response', analysisResponse);
    
    // Step 6: Check analysis result
    if (!analysisResponse || !analysisResponse.success) {
      throw new Error(analysisResponse?.error || 'Analysis failed. Please try again.');
    }
    
    // Step 7: Display results
    log('Displaying results...');
    displayResults(analysisResponse.result);
    
    // Step 8: Update badge
    try {
      chrome.runtime.sendMessage({
        action: 'updateBadge',
        score: analysisResponse.result.score
      });
    } catch (badgeError) {
      log('Badge update failed', badgeError);
      // Non-critical, continue
    }
    
    // Step 9: Cache results
    cacheResults(analysisResponse.result);
    
    log('Analysis complete!');
    
  } catch (error) {
    log('Analysis error', error);
    showError(error.message, error);
  }
}

// Display analysis results
function displayResults(result) {
  log('Displaying results', result);
  
  hideLoading();
  hideError();
  hideInitialState();
  resultsEl.classList.remove('hidden');
  
  // Update score
  const score = result.score || 0;
  scoreValueEl.textContent = score;
  
  // Update score circle color
  scoreCircleEl.className = 'score-circle';
  if (score >= 70) {
    scoreCircleEl.classList.add('trustworthy');
  } else if (score < 40) {
    scoreCircleEl.classList.add('misinformation');
  } else {
    scoreCircleEl.classList.add('suspicious');
  }
  
  // Update status badge
  const label = result.label || 'unknown';
  statusBadgeEl.textContent = label.toUpperCase();
  statusBadgeEl.className = 'status-badge ' + label;
  
  // Update confidence
  const confidence = result.confidence || 0.5;
  confidenceEl.textContent = `Confidence: ${Math.round(confidence * 100)}%`;
  
  // Update summary
  const summary = generateSummary(result);
  summaryTextEl.textContent = summary;
  
  // Update evidence
  displayEvidence(result.evidence || []);
  
  // Enable full report button
  currentReportId = result.reportId;
  fullReportBtn.disabled = !currentReportId;
}

// Generate summary text
function generateSummary(result) {
  const score = result.score || 0;
  const evidenceCount = result.evidence?.length || 0;
  
  if (score >= 70) {
    return `This content appears to be trustworthy based on our analysis. We found ${evidenceCount} supporting sources from reliable outlets. The language patterns and content structure suggest credible information.`;
  } else if (score >= 40) {
    return `This content should be viewed with caution. Our analysis found mixed signals. We recommend cross-referencing with additional trusted sources before accepting the information as accurate.`;
  } else {
    return `Warning: This content shows multiple signs of potential misinformation or manipulation. Our analysis detected red flags in language patterns, claims, or media content. Please verify with trusted sources.`;
  }
}

// Display evidence links
function displayEvidence(evidence) {
  evidenceListEl.innerHTML = '';
  
  if (!evidence || evidence.length === 0) {
    evidenceListEl.innerHTML = '<p class="no-evidence">No evidence sources found. This may indicate limited information available for verification.</p>';
    return;
  }
  
  evidence.forEach(item => {
    const evidenceItem = document.createElement('div');
    evidenceItem.className = 'evidence-item';
    
    const url = item.url || '#';
    const source = item.source || 'Unknown Source';
    const snippet = item.snippet || 'No description available';
    
    evidenceItem.innerHTML = `
      <a href="${url}" target="_blank" class="evidence-link">
        <strong>📰 ${source}</strong>
        <p>${snippet}</p>
        <span class="external-link">↗</span>
      </a>
    `;
    
    evidenceListEl.appendChild(evidenceItem);
  });
}

// Open full report
function openFullReport() {
  if (currentReportId) {
    const reportUrl = `${API_BASE_URL}/report/${currentReportId}`;
    chrome.tabs.create({ url: reportUrl });
  }
}

// Show loading state
function showLoading() {
  loadingEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  resultsEl.classList.add('hidden');
  initialStateEl?.classList.add('hidden');
}

// Hide loading state
function hideLoading() {
  loadingEl.classList.add('hidden');
}

// Hide initial state
function hideInitialState() {
  initialStateEl?.classList.add('hidden');
}

// Show error with helpful context
function showError(message, error = null) {
  log('Showing error', { message, error });
  
  hideLoading();
  hideInitialState();
  resultsEl.classList.add('hidden');
  
  // Enhance error message with helpful context
  let displayMessage = message;
  let helpfulTip = '';
  
  if (message.includes('Backend') || message.includes('connect') || message.includes('fetch')) {
    displayMessage = '❌ Cannot connect to backend server';
    helpfulTip = 'Please start the backend:\n\n1. Open terminal\n2. Navigate to backend folder\n3. Run: python app.py\n4. Wait for "Uvicorn running" message\n5. Click Retry';
  } else if (message.includes('Chrome internal') || message.includes('browser internal')) {
    displayMessage = '⛔ Cannot analyze this page';
    helpfulTip = 'Extensions cannot run on browser internal pages (chrome://, edge://, etc.).\n\nTry analyzing:\n• News websites (bbc.com, reuters.com)\n• Social media posts\n• Blog articles';
  } else if (message.includes('Not enough text')) {
    displayMessage = '📄 Not enough content';
    helpfulTip = 'This page needs at least 50 characters of text to analyze.\n\nTry:\n• A full article or blog post\n• A social media post with text\n• A news story';
  } else if (message.includes('extract page content')) {
    displayMessage = '🔧 Content extraction failed';
    helpfulTip = 'Try these steps:\n1. Refresh the page (F5)\n2. Reload the extension\n3. Click Retry';
  }
  
  errorMessageEl.textContent = displayMessage;
  
  if (helpfulTip) {
    const tipEl = document.createElement('p');
    tipEl.className = 'error-tip';
    tipEl.textContent = helpfulTip;
    errorMessageEl.appendChild(document.createElement('br'));
    errorMessageEl.appendChild(tipEl);
  }
  
  errorEl.classList.remove('hidden');
}

// Hide error
function hideError() {
  errorEl.classList.add('hidden');
}

// Show debug info
function showDebugInfo() {
  debugContentEl.innerHTML = '';
  
  // Add debug information
  addDebugInfo('Logs Count', debugLogs.length);
  addDebugInfo('API Base URL', API_BASE_URL);
  addDebugInfo('Current Report ID', currentReportId || 'None');
  
  // Add recent logs
  const recentLogs = debugLogs.slice(-10);
  recentLogs.forEach((log, index) => {
    addDebugInfo(`Log ${index + 1}`, {
      time: log.timestamp,
      message: log.message,
      data: log.data
    });
  });
  
  debugInfoEl.classList.remove('hidden');
}

// Hide debug info
function hideDebugInfo() {
  debugInfoEl.classList.add('hidden');
}

// Cache results
function cacheResults(result) {
  try {
    chrome.storage.local.set({ lastAnalysis: result, lastAnalysisTime: Date.now() }, () => {
      log('Results cached');
    });
  } catch (error) {
    log('Failed to cache results', error);
  }
}

// Load cached results
function loadCachedResults() {
  try {
    chrome.storage.local.get(['lastAnalysis', 'lastAnalysisTime'], (data) => {
      if (data.lastAnalysis) {
        const age = Date.now() - (data.lastAnalysisTime || 0);
        const ageMinutes = Math.floor(age / 60000);
        
        log('Loading cached results', { ageMinutes });
        
        // Only show cached results if less than 1 hour old
        if (ageMinutes < 60) {
          displayResults(data.lastAnalysis);
        } else {
          log('Cached results too old, showing initial state');
          initialStateEl?.classList.remove('hidden');
        }
      } else {
        log('No cached results');
        initialStateEl?.classList.remove('hidden');
      }
    });
  } catch (error) {
    log('Failed to load cached results', error);
    initialStateEl?.classList.remove('hidden');
  }
}

// Log when popup is fully loaded
log('Popup script fully loaded and ready');