# RealityFix - Real-Time Misinformation Detection Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

RealityFix is an intelligent browser extension and API platform that detects misinformation, manipulated media, and deepfakes in real-time. Powered by machine learning models, it analyzes text, images, and audio content to help users navigate the modern information landscape with confidence.

## Overview

In an era of widespread misinformation and AI-generated content, RealityFix provides automated, real-time verification of digital content. The platform combines multiple detection techniques—natural language processing, computer vision, and audio analysis—to assess content authenticity and provide evidence-based trust scores.

## Key Features

### Multi-Modal Detection
- **Text Analysis**: BERT-based classification for fake news and misleading content
- **Image Verification**: CNN-powered detection of AI-generated and manipulated images
- **Audio Authentication**: Deepfake detection using mel-spectrogram analysis
- **Evidence Retrieval**: Automated cross-referencing with trusted news sources

### Browser Integration
- **Chrome Extension**: One-click analysis of any webpage
- **Real-Time Scoring**: Instant trust scores (0-100) with color-coded indicators
- **Evidence Links**: Direct citations to authoritative sources
- **Privacy-First**: Local processing with no persistent data collection

### Developer API
- **RESTful Endpoints**: Programmatic access to all detection capabilities
- **Batch Processing**: Analyze multiple content pieces simultaneously
- **Report Generation**: Detailed analysis reports with unique identifiers
- **Interactive Documentation**: Auto-generated OpenAPI/Swagger docs

## Architecture
```
realityfix/
├── extension/              # Browser Extension (Manifest V3)
│   ├── manifest.json      # Extension configuration
│   ├── background.js      # Service worker for API communication
│   ├── content.js         # DOM content extraction
│   ├── popup.html/js      # User interface
│   ├── styles.css         # UI styling
│   └── icons/             # Extension assets
│
├── backend/               # FastAPI Backend
│   ├── app.py            # Main application server
│   ├── model_loader.py   # ML model management
│   ├── text_detector.py  # Text misinformation detection
│   ├── image_detector.py # Image manipulation detection
│   ├── audio_detector.py # Audio deepfake detection
│   ├── evidence_retriever.py  # Evidence search engine
│   ├── database.py       # SQLite persistence layer
│   └── models/           # Pretrained model storage
│
└── tests/                # Testing suite
    ├── test_api.py       # API endpoint tests
    ├── example_inputs/   # Sample test data
    └── test_results/     # Test output logs
```

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser (version 88+)
- pip package manager
- Git

## Installation

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/abhi3114-glitch/REALITYFIX.git
cd REALITYFIX/backend
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download ML models** (first run only)
```bash
python model_loader.py
```

5. **Start the backend server**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API server will be available at `http://localhost:8000`

Verify the server is running:
```bash
curl http://localhost:8000/health
```

### Chrome Extension Setup

1. **Open Chrome Extensions page**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right corner)

2. **Load the extension**
   - Click "Load unpacked"
   - Navigate to and select the `extension/` directory

3. **Verify installation**
   - The RealityFix icon should appear in your Chrome toolbar
   - Click the icon to open the analysis interface

### Verification

Run the test suite to verify installation:
```bash
cd tests
python test_api.py
```

## Usage

### Browser Extension

1. **Analyze a webpage**
   - Navigate to any news article or social media post
   - Click the RealityFix extension icon
   - Click "Analyze Page"
   - View trust score and detailed analysis

2. **Understanding trust scores**
   - **70-100 (Green)**: Trustworthy content with strong evidence
   - **40-69 (Orange)**: Questionable content requiring verification
   - **0-39 (Red)**: High likelihood of misinformation

3. **Review evidence**
   - Click evidence links to view supporting sources
   - Access full report for detailed analysis breakdown

### API Usage

#### Text Analysis
```bash
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking news: Scientists discover new planet in our solar system"
  }'
```

**Response:**
```json
{
  "score": 0.23,
  "label": "misinformation",
  "confidence": 0.87,
  "evidence": [
    {
      "url": "https://www.nasa.gov/planetary-science",
      "source": "NASA",
      "snippet": "No new planets have been discovered in our solar system since 2006..."
    }
  ],
  "explanation": "Content contradicts established scientific consensus",
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Image Analysis
```bash
curl -X POST http://localhost:8000/analyze/image \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/suspicious-image.jpg"
  }'
```

#### Audio Analysis
```bash
curl -X POST http://localhost:8000/analyze/audio \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio-clip.mp3"
  }'
```

#### Retrieve Analysis Report
```bash
curl http://localhost:8000/report/{report_id}
```

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Technical Implementation

### Text Detection Pipeline
1. **Preprocessing**: Tokenization and text normalization
2. **Embedding**: BERT-based contextual embeddings
3. **Classification**: Fine-tuned transformer model
4. **Evidence Retrieval**: Cross-reference with trusted sources
5. **Scoring**: Weighted confidence aggregation

### Image Detection Pipeline
1. **Acquisition**: Download and validate image
2. **Preprocessing**: Resize and normalize pixel values
3. **Feature Extraction**: CNN-based artifact detection
4. **Pattern Analysis**: Identify AI generation signatures
5. **Classification**: Authenticity probability scoring

### Audio Detection Pipeline
1. **Acquisition**: Download and validate audio file
2. **Preprocessing**: Resample to 16kHz, mono channel
3. **Feature Extraction**: Mel-spectrogram generation
4. **Analysis**: CNN-based deepfake pattern detection
5. **Classification**: Authenticity confidence scoring

## Security & Privacy

- **No Persistent Storage**: Analysis results are not permanently stored
- **Local Processing**: ML inference runs on your server
- **HTTPS Only**: Extension requires secure connections
- **No Tracking**: Zero telemetry or user behavior tracking
- **Open Source**: Fully auditable codebase

## Current Limitations

### MVP Constraints
- **Model Accuracy**: General-purpose models; specialized fine-tuning pending
- **Evidence Retrieval**: Mock implementation; production requires API integration
- **Language Support**: Currently optimized for English content
- **Initial Latency**: First analysis slower due to model loading
- **Audio Formats**: Limited to common formats (MP3, WAV, OGG)

### Known Issues
- Large image files (>10MB) may timeout
- Video analysis limited to extracted audio tracks
- Evidence retrieval returns simulated data in MVP

## Development

### Running in Development Mode

**Backend with auto-reload:**
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Extension development:**
- Modify extension files as needed
- Navigate to `chrome://extensions/`
- Click "Reload" button for the RealityFix extension
- Test changes immediately

### Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-detector`
3. Implement changes with tests
4. Commit with descriptive messages: `git commit -m 'Add video frame analysis'`
5. Push to your fork: `git push origin feature/new-detector`
6. Submit a Pull Request with detailed description

### Adding New Features

**New ML Model:**
```python
# In model_loader.py
def load_new_model():
    model = AutoModel.from_pretrained("model-name")
    return model

# In app.py
@app.post("/analyze/newtype")
async def analyze_newtype(data: NewTypeRequest):
    result = new_detector.analyze(data)
    return result
```

## Roadmap

### Phase 1: Enhanced Accuracy (Q2 2024)
- Fine-tune models on fact-checking datasets
- Implement multi-language support (ES, FR, DE, ZH)
- Integrate real-time news API (Google News, Bing)

### Phase 2: Advanced Features (Q3 2024)
- Full video content analysis
- User feedback and crowdsourced verification
- Browser support: Firefox, Safari, Edge

### Phase 3: Scale & Deploy (Q4 2024)
- Cloud deployment (AWS/GCP/Azure)
- API rate limiting and authentication
- User accounts with analysis history
- Publish to Chrome Web Store

### Phase 4: Enterprise (2025)
- Collaborative fact-checking dashboard
- Organization-level API access
- Custom model training for specific domains
- Mobile applications (iOS, Android)

## Testing

Run the complete test suite:
```bash
cd tests
python test_api.py
```

Test individual endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Text analysis
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Test content"}'
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **HuggingFace**: Pretrained transformer models and tokenizers
- **FastAPI**: High-performance web framework
- **Chrome Extensions Team**: Comprehensive Manifest V3 documentation
- **Open-source ML Community**: Foundational research and models

## Support

- **Issues**: [GitHub Issues](https://github.com/abhi3114-glitch/REALITYFIX/issues)
- **Discussions**: [GitHub Discussions](https://github.com/abhi3114-glitch/REALITYFIX/discussions)
- **Documentation**: [Wiki](https://github.com/abhi3114-glitch/REALITYFIX/wiki)

## Citation

If you use RealityFix in your research or project, please cite:
```bibtex
@software{realityfix2024,
  author = {Abhi},
  title = {RealityFix: Real-Time Misinformation Detection Platform},
  year = {2024},
  url = {https://github.com/abhi3114-glitch/REALITYFIX}
}
```

---

**Building a more trustworthy information ecosystem, one analysis at a time.**
