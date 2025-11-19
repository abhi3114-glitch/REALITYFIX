# RealityFix Architecture Documentation

## System Overview

RealityFix is a distributed system consisting of three main components:

1. **Browser Extension** (Frontend)
2. **Backend API** (FastAPI)
3. **ML Models** (PyTorch/Transformers)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser Extension                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Content.js  │  │ Background.js│  │  Popup.js    │     │
│  │  (Extract)   │→ │  (Analyze)   │→ │  (Display)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                      Backend API (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   app.py     │  │   Database   │  │   Evidence   │     │
│  │  (Routes)    │→ │  (SQLite)    │  │  (Retriever) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                                                    │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────┐      │
│  │              ML Detection Layer                   │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │      │
│  │  │   Text   │  │  Image   │  │  Audio   │       │      │
│  │  │ Detector │  │ Detector │  │ Detector │       │      │
│  │  └──────────┘  └──────────┘  └──────────┘       │      │
│  └──────────────────────────────────────────────────┘      │
│         │                                                    │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────┐      │
│  │              Model Loader                         │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │      │
│  │  │   BERT   │  │  ResNet  │  │   CNN    │       │      │
│  │  │  (Text)  │  │ (Image)  │  │ (Audio)  │       │      │
│  │  └──────────┘  └──────────┘  └──────────┘       │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Browser Extension

#### Content Script (content.js)
- **Purpose**: Extracts content from web pages
- **Execution**: Runs on every webpage
- **Functions**:
  - `extractPageText()`: Gets first 5000 characters
  - `extractImages()`: Collects image URLs (max 10)
  - `extractVideos()`: Identifies video content
- **Communication**: Message passing with background script

#### Background Script (background.js)
- **Purpose**: Service worker for API communication
- **Functions**:
  - `analyzeContent()`: Orchestrates analysis
  - `analyzeText()`: Calls text API
  - `analyzeImage()`: Calls image API
  - `calculateCombinedScore()`: Merges results
  - `updateBadge()`: Updates extension icon
- **Storage**: Chrome storage API for caching

#### Popup UI (popup.html/js)
- **Purpose**: User interface for results
- **Features**:
  - Trust score visualization
  - Evidence links display
  - Full report access
  - Manual analysis trigger
- **State Management**: Local storage + Chrome storage

### 2. Backend API

#### Main Application (app.py)
- **Framework**: FastAPI
- **Endpoints**:
  - `GET /`: Health check
  - `POST /analyze/text`: Text analysis
  - `POST /analyze/image`: Image analysis
  - `POST /analyze/audio`: Audio analysis
  - `GET /report/{id}`: Report retrieval
  - `GET /health`: System health
- **Middleware**: CORS for browser extension
- **Error Handling**: HTTPException with detailed messages

#### Text Detector (text_detector.py)
- **Model**: DistilBERT (fine-tuned)
- **Process**:
  1. Tokenization (max 512 tokens)
  2. Model inference
  3. Softmax probabilities
  4. Score calculation
  5. Label assignment
- **Fallback**: Heuristic-based analysis
- **Output**: Score, label, confidence, explanation

#### Image Detector (image_detector.py)
- **Model**: ResNet-18 (pretrained)
- **Process**:
  1. Image download
  2. Preprocessing (resize, normalize)
  3. Feature extraction
  4. Artifact detection
  5. Authenticity scoring
- **Techniques**:
  - Statistical analysis
  - Artifact detection
  - Forensic heuristics
- **Output**: Score, label, confidence, explanation

#### Audio Detector (audio_detector.py)
- **Model**: Simple CNN
- **Process**:
  1. Audio download
  2. Resampling (16kHz)
  3. Mel spectrogram extraction
  4. CNN inference
  5. Deepfake scoring
- **Features**:
  - 128 mel bands
  - Log scale transformation
  - Fixed-size input (128x128)
- **Output**: Score, label, confidence, explanation

#### Evidence Retriever (evidence_retriever.py)
- **Purpose**: Find supporting evidence
- **Sources**: BBC, Reuters, AP News, Wikipedia
- **Implementation**: Mock search (MVP)
- **Future**: Bing API, Google Custom Search
- **Output**: List of evidence items (URL, source, snippet)

#### Database (database.py)
- **Type**: SQLite (async)
- **Tables**:
  - `reports`: Analysis results
  - `user_flags`: User feedback
  - `cache`: Cached results
- **Operations**:
  - Save report
  - Get report
  - Add user flag
  - Cache management
- **Indexes**: Optimized queries

#### Model Loader (model_loader.py)
- **Purpose**: Centralized model management
- **Features**:
  - Model caching
  - Device selection (CPU/GPU)
  - Lazy loading
- **Models**:
  - Text: HuggingFace transformers
  - Image: torchvision models
  - Audio: Custom CNN

## Data Flow

### Text Analysis Flow
```
1. User clicks "Analyze Page"
2. Popup → Content Script: Extract text
3. Content Script → Background: Send text
4. Background → Backend API: POST /analyze/text
5. Backend → Text Detector: Analyze
6. Text Detector → Model: Inference
7. Backend → Evidence Retriever: Search
8. Backend → Database: Save report
9. Backend → Background: Return results
10. Background → Popup: Display results
11. Background → Badge: Update icon
```

### Image Analysis Flow
```
1. Background extracts image URLs
2. Background → Backend API: POST /analyze/image
3. Backend → Image Detector: Download & analyze
4. Image Detector → Model: Feature extraction
5. Image Detector → Artifact Detection: Check
6. Backend → Database: Save report
7. Backend → Background: Return results
8. Background → Popup: Display results
```

## Security Considerations

### Extension Security
- **Manifest V3**: Latest security standards
- **Content Security Policy**: Strict CSP
- **Permissions**: Minimal required permissions
- **HTTPS Only**: Secure connections only

### API Security
- **CORS**: Configured for extension origin
- **Input Validation**: Pydantic models
- **Rate Limiting**: To be implemented
- **Authentication**: To be added for production

### Data Privacy
- **No Persistent Storage**: Analysis not stored permanently
- **Local Processing**: Models run on your server
- **No Tracking**: No user data collection
- **Encrypted Transit**: HTTPS required

## Performance Optimization

### Model Loading
- **Lazy Loading**: Models loaded on first use
- **Caching**: Models cached in memory
- **Device Selection**: Automatic GPU detection

### API Performance
- **Async Operations**: FastAPI async endpoints
- **Connection Pooling**: HTTP client reuse
- **Database Indexing**: Optimized queries

### Extension Performance
- **Content Script**: Minimal DOM access
- **Background Script**: Efficient message handling
- **Popup**: Cached results display

## Scalability

### Current Limitations
- Single server deployment
- In-memory model caching
- SQLite database

### Future Scaling
- **Horizontal Scaling**: Multiple API servers
- **Load Balancing**: Nginx/HAProxy
- **Database**: PostgreSQL/MongoDB
- **Caching**: Redis
- **Message Queue**: RabbitMQ/Kafka
- **CDN**: Static asset delivery

## Error Handling

### Extension Errors
- Network failures → Retry logic
- API errors → User-friendly messages
- Timeout → Graceful degradation

### API Errors
- Model loading failures → Fallback analysis
- Database errors → In-memory fallback
- External API failures → Mock data

## Monitoring & Logging

### Logging Levels
- **INFO**: Normal operations
- **WARNING**: Fallback usage
- **ERROR**: Failures

### Metrics to Track
- Analysis success rate
- Response times
- Model accuracy
- User feedback

## Testing Strategy

### Unit Tests
- Model loading
- Detector functions
- Database operations
- API endpoints

### Integration Tests
- End-to-end analysis flow
- Extension ↔ API communication
- Database persistence

### Performance Tests
- Load testing
- Stress testing
- Response time benchmarks

## Deployment

### Development
```bash
# Backend
python backend/app.py

# Extension
Load unpacked in chrome://extensions/
```

### Production
```bash
# Backend with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app

# Extension
Package and submit to Chrome Web Store
```

## Future Architecture

### Microservices
- Text analysis service
- Image analysis service
- Audio analysis service
- Evidence service
- Report service

### Cloud Deployment
- **Compute**: AWS EC2/Lambda, GCP Compute
- **Storage**: S3, Cloud Storage
- **Database**: RDS, Cloud SQL
- **ML**: SageMaker, Vertex AI

### Real-time Features
- WebSocket connections
- Live analysis updates
- Collaborative fact-checking