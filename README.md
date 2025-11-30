# RealityFix - Real-Time Fake News & Manipulated Media Detector

![RealityFix](https://img.shields.io/badge/RealityFix-v1.0.0-blue)
realityfix/
├── extension/                  # Browser Extension
│   ├── manifest.json          # Chrome extension manifest V3
│   ├── background.js          # Service worker for API communication
│   ├── content.js             # Content script for data extraction
│   ├── popup.html             # Popup UI
│   ├── popup.js               # Popup logic
│   ├── styles.css             # Popup styling
│   └── icons/                 # Extension icons
├── backend/                    # FastAPI Backend
│   ├── app.py                 # Main FastAPI application
│   ├── model_loader.py        # ML model management
│   ├── text_detector.py       # Text misinformation detection
│   ├── image_detector.py      # Image manipulation detection
│   ├── audio_detector.py      # Audio deepfake detection
│   ├── evidence_retriever.py  # Evidence search module
│   ├── database.py            # SQLite database operations
│   ├── requirements.txt       # Python dependencies
│   └── models/                # Pretrained models directory
├── tests/                      # Testing
│   ├── test_api.py            # API testing examples
│   ├── example_inputs/        # Sample test data
│   └── test_results/          # Test outputs
└── README.md                   # This file
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser
- pip (Python package manager)
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/abhi3114-glitch/REALITYFIX.git
cd REALITYFIX
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right corner)

2. **Load the extension**
   - Click "Load unpacked"
   - Select the `extension/` directory from the project

3. **Verify installation**
   - You should see the RealityFix icon in your Chrome toolbar
   - Click it to open the popup interface

### Testing the Setup

1. **Test the API**
```bash
cd tests
python test_api.py
```

2. **Test the extension**
   - Navigate to any news website
   - Click the RealityFix extension icon
   - Click "Analyze Page" button
   - View the trust score and analysis results

## 📖 Usage Guide

### Using the Browser Extension

1. **Automatic Analysis**
   - Browse to any webpage
   - The extension automatically extracts content
   - Click the extension icon to view results

2. **Manual Analysis**
   - Click the RealityFix icon
   - Click "Analyze Page" button
   - Wait for analysis to complete (5-10 seconds)

3. **Understanding Results**
   - **Trust Score (0-100)**:
     - 70-100: Trustworthy (Green)
     - 40-69: Suspicious (Orange)
     - 0-39: Misinformation (Red)
   - **Evidence Links**: Click to verify claims with trusted sources
   - **Full Report**: Click to view detailed analysis

### Using the API

#### Text Analysis
```bash
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text content here"}'
```

**Response:**
```json
{
  "score": 0.85,
  "label": "trustworthy",
  "confidence": 0.92,
  "evidence": [
    {
      "url": "https://www.reuters.com/...",
      "source": "Reuters",
      "snippet": "Supporting evidence..."
    }
  ],
  "explanation": "The text appears credible...",
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Image Analysis
```bash
curl -X POST http://localhost:8000/analyze/image \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

#### Audio Analysis
```bash
curl -X POST http://localhost:8000/analyze/audio \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "https://example.com/audio.mp3"}'
```

#### Get Report
```bash
curl http://localhost:8000/report/{report_id}
```

## 🔬 Technical Details

### Text Detection Algorithm
1. **Preprocessing**: Tokenization and normalization
2. **Feature Extraction**: BERT embeddings
3. **Classification**: Transformer-based classification
4. **Evidence Retrieval**: Search trusted sources
5. **Score Calculation**: Weighted combination of signals

### Image Detection Algorithm
1. **Download**: Fetch image from URL
2. **Preprocessing**: Resize and normalize
3. **Feature Extraction**: CNN-based features
4. **Artifact Detection**: Check for AI generation patterns
5. **Classification**: Authenticity scoring

### Audio Detection Algorithm
1. **Download**: Fetch audio file
2. **Preprocessing**: Resample to 16kHz
3. **Feature Extraction**: Mel spectrogram
4. **Analysis**: CNN-based deepfake detection
5. **Classification**: Authenticity scoring

## 🔐 Security & Privacy

- **No Data Collection**: Content is analyzed in real-time and not stored permanently
- **Local Processing**: ML models run on your server
- **HTTPS Required**: Extension only works on secure connections
- **API Authentication**: Can be added for production use

## ⚠️ Limitations

### Current MVP Limitations
1. **Model Accuracy**: Uses general-purpose models, not specialized fact-checking models
2. **Evidence Retrieval**: Mock implementation for MVP (needs API keys for production)
3. **Language Support**: Currently optimized for English only
4. **Performance**: First analysis may be slow due to model loading
5. **Audio Analysis**: Requires audio files in common formats (MP3, WAV)

### Known Issues
- Large images may take longer to analyze
- Video analysis limited to YouTube transcripts
- Evidence retrieval returns mock data (needs API integration)

## 🚧 Future Enhancements

### Planned Features
1. **Multi-language Support**: Extend to Spanish, French, German, etc.
2. **Real-time Evidence**: Integrate with Bing/Google News API
3. **Advanced ML Models**: Fine-tuned models for fact-checking
4. **Video Analysis**: Full video content analysis
5. **User Feedback**: Allow users to report false positives/negatives
6. **Browser Support**: Firefox, Safari, Edge extensions
7. **Mobile App**: iOS and Android applications
8. **API Rate Limiting**: Implement rate limiting for production
9. **User Accounts**: Save analysis history
10. **Collaborative Fact-checking**: Community-driven verification

### Production Roadmap
1. **Phase 1**: Improve model accuracy with fine-tuning
2. **Phase 2**: Integrate real search APIs
3. **Phase 3**: Add user authentication and history
4. **Phase 4**: Deploy to cloud (AWS/GCP/Azure)
5. **Phase 5**: Publish to Chrome Web Store

## 🛠️ Development

### Running in Development Mode

**Backend with auto-reload:**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Extension development:**
- Make changes to extension files
- Click "Reload" button in `chrome://extensions/`
- Test changes immediately

### Adding New Features

1. **New ML Model**:
   - Add model loading code in `model_loader.py`
   - Create detector class (e.g., `video_detector.py`)
   - Add API endpoint in `app.py`

2. **New Evidence Source**:
   - Update `TRUSTED_SOURCES` in `evidence_retriever.py`
   - Implement search integration
   - Update UI to display new sources

### Testing

```bash
# Run API tests
python tests/test_api.py

# Test specific endpoint
curl http://localhost:8000/health
```

## 📊 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Abhi** - Initial work - [abhi3114-glitch](https://github.com/abhi3114-glitch)

## 🙏 Acknowledgments

- HuggingFace for pretrained transformer models
- FastAPI for the excellent web framework
- Chrome Extensions team for comprehensive documentation
- Open-source ML community

## 📞 Support

For issues, questions, or suggestions:
- **GitHub Issues**: https://github.com/abhi3114-glitch/REALITYFIX/issues
- **Email**: support@realityfix.com (placeholder)

## 🔗 Links

- **GitHub Repository**: https://github.com/abhi3114-glitch/REALITYFIX
- **Documentation**: Coming soon
- **Demo Video**: Coming soon

---

**Built with ❤️ for a more trustworthy internet**