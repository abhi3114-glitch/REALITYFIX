# RealityFix MVP - Development Todo List

## Project Structure
```
realityfix/
├── extension/                  # Browser Extension
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   ├── popup.html
│   ├── popup.js
│   ├── styles.css
│   └── icons/
├── backend/                    # FastAPI Backend
│   ├── app.py
│   ├── model_loader.py
│   ├── text_detector.py
│   ├── image_detector.py
│   ├── audio_detector.py
│   ├── evidence_retriever.py
│   ├── database.py
│   ├── requirements.txt
│   └── models/                 # Pretrained models directory
├── tests/                      # Test files and examples
│   ├── test_api.py
│   ├── example_inputs/
│   └── test_results/
└── README.md
```

## Files to Create (8 core files + supporting files)

### Browser Extension (3 files)
1. ✅ extension/manifest.json - Chrome extension manifest V3
2. ✅ extension/popup.html - Popup UI with trust score display
3. ✅ extension/popup.js - Popup logic and API communication
4. ✅ extension/content.js - Content script for data extraction
5. ✅ extension/background.js - Service worker for background tasks
6. ✅ extension/styles.css - Styling for popup

### Backend API (7 files)
7. ✅ backend/app.py - FastAPI main application with all routes
8. ✅ backend/model_loader.py - Load pretrained ML models
9. ✅ backend/text_detector.py - Text misinformation detection
10. ✅ backend/image_detector.py - AI-generated image detection
11. ✅ backend/audio_detector.py - Deepfake audio detection
12. ✅ backend/evidence_retriever.py - Evidence search from trusted sources
13. ✅ backend/database.py - SQLite database operations
14. ✅ backend/requirements.txt - Python dependencies

### Documentation & Setup
15. ✅ README.md - Complete setup and usage guide
16. ✅ tests/test_api.py - API testing examples

## Implementation Notes
- Use pretrained models: transformers for text, image forensics for images, ResNet for audio
- Evidence retrieval using web search APIs
- SQLite for simple data persistence
- Chrome Manifest V3 for extension
- FastAPI for high-performance backend
- All code fully commented and production-ready