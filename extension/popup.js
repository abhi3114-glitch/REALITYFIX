const BASE_URL = 'http://localhost:8000';

// DOM Elements
const views = {
  initial: document.getElementById('initialState'),
  loading: document.getElementById('loadingState'),
  results: document.getElementById('resultsState'),
  error: document.getElementById('errorState')
};

const buttons = {
  start: document.getElementById('startAnalyzeBtn'),
  reset: document.getElementById('resetBtn'),
  retry: document.getElementById('retryBtn')
};

const display = {
  scoreValue: document.getElementById('scoreValue'),
  gaugeProgress: document.getElementById('gaugeProgress'),
  verdictBadge: document.getElementById('verdictBadge'),
  explanation: document.getElementById('explanationText'),
  domain: document.getElementById('domainValue'),
  ling: document.getElementById('lingValue'),
  ml: document.getElementById('mlValue'),
  meta: document.getElementById('metaValue'),
  backendStatus: document.getElementById('backendStatus'),
  errorText: document.getElementById('errorText')
};

// State
let currentTab = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  checkBackendStatus();

  // Get current tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tab;

  // Event Listeners
  buttons.start.addEventListener('click', startAnalysis);
  buttons.reset.addEventListener('click', () => switchView('initial'));
  buttons.retry.addEventListener('click', startAnalysis);
});

async function checkBackendStatus() {
  try {
    const response = await fetch(`${BASE_URL}/health`);
    if (response.ok) {
      display.backendStatus.classList.add('online');
      display.backendStatus.title = "Backend Online";
    }
  } catch (e) {
    display.backendStatus.classList.remove('online');
    display.backendStatus.title = "Backend Offline";
  }
}

function switchView(viewName) {
  Object.values(views).forEach(el => el.classList.add('hidden'));
  views[viewName].classList.remove('hidden');
}

async function startAnalysis() {
  switchView('loading');

  try {
    // 1. Get page content
    const content = await getPageContent();

    // 2. Send to backend
    const result = await analyzeContent(content);

    // 3. Show results
    showResults(result);

  } catch (error) {
    console.error('Analysis failed:', error);
    showError(error.message);
  }
}

function getPageContent() {
  return new Promise((resolve, reject) => {
    if (!currentTab?.id) {
      reject(new Error('No active tab found'));
      return;
    }

    // Execute script to get text
    chrome.scripting.executeScript({
      target: { tabId: currentTab.id },
      func: () => {
        // Smart text extraction
        function getMainContent() {
          // 1. Try to find the main article content
          const selectors = ['article', 'main', '[role="main"]', '.post-content', '.article-body', '#content'];
          for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element && element.innerText.length > 500) {
              return element.innerText;
            }
          }

          // 2. Fallback: Aggregate paragraphs
          const paragraphs = Array.from(document.getElementsByTagName('p'));
          const mainText = paragraphs
            .map(p => p.innerText.trim())
            .filter(text => text.length > 50) // Filter out short snippets (nav, ads)
            .join('\n\n');

          if (mainText.length > 200) {
            return mainText;
          }

          // 3. Last resort: Body text
          return document.body.innerText;
        }

        return {
          text: getMainContent(),
          url: window.location.href,
          title: document.title
        };
      }
    }, (results) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }

      if (!results || !results[0] || !results[0].result) {
        reject(new Error('Could not extract page content'));
        return;
      }

      resolve(results[0].result);
    });
  });
}

async function analyzeContent(content) {
  const response = await fetch(`${BASE_URL}/analyze/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: content.text,
      url: content.url
    })
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  return await response.json();
}

function showResults(data) {
  // Update Score Gauge
  const score = data.score; // 0 to 1
  const percentage = Math.round(score * 100);

  // Animate Gauge
  // Arc length is ~126. Offset = 126 - (126 * score)
  const offset = 126 - (126 * score);
  display.gaugeProgress.style.strokeDashoffset = offset;

  // Color based on score
  let color = 'var(--danger)';
  let verdict = 'MISINFORMATION';
  let className = 'misinformation';

  if (score >= 0.7) {
    color = 'var(--success)';
    verdict = 'TRUSTWORTHY';
    className = 'trustworthy';
  } else if (score >= 0.4) {
    color = 'var(--warning)';
    verdict = 'SUSPICIOUS';
    className = 'suspicious';
  }

  display.gaugeProgress.style.stroke = color;
  display.scoreValue.textContent = percentage;
  display.scoreValue.style.color = color;

  display.verdictBadge.textContent = verdict;
  display.verdictBadge.className = 'verdict-badge ' + className;
  display.verdictBadge.style.backgroundColor = '';
  display.verdictBadge.style.color = '';

  // Update Details
  display.explanation.textContent = data.explanation;

  // Breakdown
  const breakdown = data.breakdown || {};

  // Helper for score display
  const getScoreDisplay = (score, type) => {
    if (score === null || score === undefined) return { text: 'N/A', color: 'var(--text-muted)' };

    if (type === 'domain') {
      if (score >= 0.9) return { text: 'Trusted', color: 'var(--success)' };
      if (score <= 0.3) return { text: 'Unsafe', color: 'var(--danger)' };
      return { text: 'Neutral', color: 'var(--warning)' };
    }

    // For other scores (0-1)
    if (score >= 0.7) return { text: 'High', color: 'var(--success)' };
    if (score >= 0.4) return { text: 'Medium', color: 'var(--warning)' };
    return { text: 'Low', color: 'var(--danger)' };
  };

  // 1. Domain
  const domain = getScoreDisplay(breakdown.domain_trust, 'domain');
  display.domain.textContent = domain.text;
  display.domain.style.color = domain.color;

  // 2. Linguistic
  const ling = getScoreDisplay(breakdown.linguistic_score, 'standard');
  display.ling.textContent = ling.text;
  display.ling.style.color = ling.color;

  // 3. AI Model
  const ml = getScoreDisplay(breakdown.ml_score, 'standard');
  display.ml.textContent = ml.text;
  display.ml.style.color = ml.color;

  // 4. Metadata
  const meta = getScoreDisplay(breakdown.metadata_score, 'standard');
  display.meta.textContent = meta.text;
  display.meta.style.color = meta.color;

  switchView('results');
}

function showError(msg) {
  display.errorText.textContent = msg;
  switchView('error');
}