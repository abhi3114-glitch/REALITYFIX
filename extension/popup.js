/**
 * Popup Script - Handles UI interactions and displays analysis results
 */

// DOM Elements
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const errorMessageEl = document.getElementById('errorMessage');
const resultsEl = document.getElementById('results');
const scoreValueEl = document.getElementById('scoreValue');
const scoreCircleEl = document.getElementById('scoreCircle');
const statusBadgeEl = document.getElementById('statusBadge');
const confidenceEl = document.getElementById('confidence');
const summaryTextEl = document.getElementById('summaryText');
const evidenceListEl = document.getElementById('evidenceList');
const fullReportBtn = document.getElementById('fullReportBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const retryBtn = document.getElementById('retryBtn');

let currentReportId = null;

// Initialize popup
document.addEventListener('DOMContentLoaded', () => {
  // Load cached results if available
  loadCachedResults();
  
  // Set up event listeners
  analyzeBtn.addEventListener('click', analyzePage);
  retryBtn.addEventListener('click', analyzePage);
  fullReportBtn.addEventListener('click', openFullReport);
});

// Analyze current page
async function analyzePage() {
  try {
    showLoading();
    
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Extract content from page
    const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractContent' });
    
    if (!response.success) {
      throw new Error('Failed to extract page content');
    }
    
    // Send to background for analysis
    const analysisResponse = await chrome.runtime.sendMessage({
      action: 'analyzeContent',
      data: response.data
    });
    
    if (!analysisResponse.success) {
      throw new Error(analysisResponse.error || 'Analysis failed');
    }
    
    // Display results
    displayResults(analysisResponse.result);
    
    // Update badge
    chrome.runtime.sendMessage({
      action: 'updateBadge',
      score: analysisResponse.result.score
    });
    
    // Cache results
    cacheResults(analysisResponse.result);
    
  } catch (error) {
    showError(error.message);
  }
}

// Display analysis results
function displayResults(result) {
  hideLoading();
  hideError();
  resultsEl.classList.remove('hidden');
  
  // Update score
  scoreValueEl.textContent = result.score;
  
  // Update score circle color
  scoreCircleEl.className = 'score-circle';
  if (result.score >= 70) {
    scoreCircleEl.classList.add('trustworthy');
  } else if (result.score < 40) {
    scoreCircleEl.classList.add('misinformation');
  } else {
    scoreCircleEl.classList.add('suspicious');
  }
  
  // Update status badge
  statusBadgeEl.textContent = result.label.toUpperCase();
  statusBadgeEl.className = 'status-badge';
  statusBadgeEl.classList.add(result.label);
  
  // Update confidence
  confidenceEl.textContent = `Confidence: ${Math.round(result.confidence * 100)}%`;
  
  // Update summary
  let summary = generateSummary(result);
  summaryTextEl.textContent = summary;
  
  // Update evidence
  displayEvidence(result.evidence);
  
  // Enable full report button
  currentReportId = result.reportId;
  fullReportBtn.disabled = !currentReportId;
}

// Generate summary text
function generateSummary(result) {
  const score = result.score;
  
  if (score >= 70) {
    return `This content appears to be trustworthy. Our analysis found ${result.evidence.length} supporting sources from reliable outlets.`;
  } else if (score >= 40) {
    return `This content should be viewed with caution. We found mixed signals and recommend verifying with additional sources.`;
  } else {
    return `Warning: This content shows signs of misinformation or manipulation. Multiple red flags detected in our analysis.`;
  }
}

// Display evidence links
function displayEvidence(evidence) {
  evidenceListEl.innerHTML = '';
  
  if (!evidence || evidence.length === 0) {
    evidenceListEl.innerHTML = '<p class="no-evidence">No evidence sources available.</p>';
    return;
  }
  
  evidence.forEach(item => {
    const evidenceItem = document.createElement('div');
    evidenceItem.className = 'evidence-item';
    
    evidenceItem.innerHTML = `
      <a href="${item.url}" target="_blank" class="evidence-link">
        <strong>${item.source}</strong>
        <p>${item.snippet}</p>
      </a>
    `;
    
    evidenceListEl.appendChild(evidenceItem);
  });
}

// Open full report
function openFullReport() {
  if (currentReportId) {
    const reportUrl = `http://localhost:8000/report/${currentReportId}`;
    chrome.tabs.create({ url: reportUrl });
  }
}

// Show loading state
function showLoading() {
  loadingEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  resultsEl.classList.add('hidden');
}

// Hide loading state
function hideLoading() {
  loadingEl.classList.add('hidden');
}

// Show error
function showError(message) {
  hideLoading();
  errorMessageEl.textContent = message;
  errorEl.classList.remove('hidden');
  resultsEl.classList.add('hidden');
}

// Hide error
function hideError() {
  errorEl.classList.add('hidden');
}

// Cache results
function cacheResults(result) {
  chrome.storage.local.set({ lastAnalysis: result });
}

// Load cached results
function loadCachedResults() {
  chrome.storage.local.get(['lastAnalysis'], (data) => {
    if (data.lastAnalysis) {
      displayResults(data.lastAnalysis);
    } else {
      resultsEl.classList.remove('hidden');
    }
  });
}