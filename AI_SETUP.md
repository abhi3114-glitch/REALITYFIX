# 🚀 RealityFix AI-Powered Setup Guide (Groq Edition)

## What's New
You now have **Ultra-Fast AI Analysis** using **Llama 3.3** via Groq! This provides instant, high-accuracy credibility checks.

## Quick Start

### Step 1: Get Your FREE API Key
1. Visit: https://console.groq.com/keys
2. Create a new API Key
3. Copy the key (starts with `gsk_`)

### Step 2: Configure
1. Open `backend/.env`
2. Add your key:
   ```
   GROQ_API_KEY=gsk_...your-actual-key...
   ```

### Step 3: Install Dependencies
```bash
cd backend
..\venv\Scripts\pip install groq
```

### Step 4: Restart Backend
```bash
# Stop current backend (Ctrl+C)
.\venv\Scripts\python backend/app.py
```

## How It Works

### NEW Flow (With Groq AI)
1. Extract text from page  
2. **Llama 3.3 analyzes for:**
   - Factual claims extraction
   - Logical consistency
   - Source credibility  
   - Bias detection
   - Missing context
3. **Fact Check API searches** for existing debunks
4. Combined analysis with confidence scores

## API Limits (Free Tier)
**Groq:**
- Extremely fast (hundreds of tokens/sec)
- Generous free tier limits

## Testing

Try analyzing these:
- **Trusted**: BBC, Reuters, New York Times articles
- **Suspicious**: Unknown blog posts, social media claims
- **Misinformation**: Known fake news sites

The AI will provide detailed, explainable results!

## Troubleshooting

**"Groq API not available"**
- Check your `.env` file has the correct `GROQ_API_KEY`
- Restart the backend

**"Analysis incomplete"**
- The system falls back to traditional analysis if AI fails
- Check internet connection
