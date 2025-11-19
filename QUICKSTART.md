# RealityFix - Quick Start Guide

Get RealityFix up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check pip
pip3 --version

# Check Chrome
google-chrome --version
```

## 5-Minute Setup

### Step 1: Clone & Navigate (30 seconds)
```bash
git clone https://github.com/abhi3114-glitch/REALITYFIX.git
cd REALITYFIX
```

### Step 2: Backend Setup (2 minutes)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Step 3: Start Backend (30 seconds)
```bash
# Still in backend directory
python app.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Load Extension (1 minute)
1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top-right toggle)
4. Click "Load unpacked"
5. Navigate to and select the `extension/` folder
6. You should see RealityFix icon appear!

### Step 5: Test It! (1 minute)
1. Go to any news website (e.g., bbc.com)
2. Click the RealityFix extension icon
3. Click "Analyze Page"
4. Wait 5-10 seconds
5. See your trust score!

## Quick Test Commands

### Test Backend API
```bash
# In a new terminal
cd tests
python test_api.py
```

### Test Individual Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Text analysis
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test article about climate change research."}'
```

## Common Issues & Fixes

### Issue: "Module not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: "Port 8000 already in use"
```bash
# Find and kill the process
# On Linux/Mac:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Extension not loading
1. Check that you selected the `extension/` folder, not the project root
2. Make sure all extension files are present
3. Check Chrome console for errors (Inspect popup → Console)

### Issue: "Connection refused" in extension
1. Make sure backend is running (`python backend/app.py`)
2. Check backend is on port 8000
3. Verify CORS is enabled in `app.py`

## What's Next?

### Customize the Extension
- Edit `extension/popup.html` for UI changes
- Modify `extension/styles.css` for styling
- Update `extension/content.js` for extraction logic

### Improve ML Models
- Fine-tune models in `backend/model_loader.py`
- Add new detection methods in detector files
- Integrate better pretrained models

### Add Features
- Implement real evidence search (replace mock in `evidence_retriever.py`)
- Add user authentication
- Create analysis history
- Add more trusted sources

## Development Workflow

```bash
# Terminal 1: Backend with auto-reload
cd backend
uvicorn app:app --reload

# Terminal 2: Run tests
cd tests
python test_api.py

# Chrome: Reload extension after changes
# Go to chrome://extensions/ → Click reload icon
```

## Production Deployment

### Backend
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### Extension
1. Create icons (16x16, 48x48, 128x128)
2. Update manifest.json with production API URL
3. Zip the extension folder
4. Submit to Chrome Web Store

## Resources

- **Full Documentation**: README.md
- **Architecture**: ARCHITECTURE.md
- **API Docs**: http://localhost:8000/docs (when running)
- **GitHub**: https://github.com/abhi3114-glitch/REALITYFIX

## Support

Having issues? Check:
1. README.md for detailed setup
2. GitHub Issues for known problems
3. API docs at /docs endpoint

## Success Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Backend running on port 8000
- [ ] Extension loaded in Chrome
- [ ] Can analyze a webpage
- [ ] API tests passing

If all checked, you're ready to go! 🚀

---

**Happy fact-checking!**