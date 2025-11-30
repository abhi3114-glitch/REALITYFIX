from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import detectors
from text_detector import ImprovedTextDetector
from image_detector import ImageDetector
from audio_detector import AudioDetector
from evidence_retriever import EvidenceRetriever
from database import Database

app = FastAPI(
    title="RealityFix API",
    description="Enhanced fake news detection with better accuracy",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components with improved detector
text_detector = ImprovedTextDetector()  # ← Using improved version
image_detector = ImageDetector()
audio_detector = AudioDetector()
evidence_retriever = EvidenceRetriever()
database = Database()

# Request/Response Models
class TextAnalysisRequest(BaseModel):
    text: str
    url: Optional[str] = None

class ImageAnalysisRequest(BaseModel):
    image_url: str

class AudioAnalysisRequest(BaseModel):
    audio_url: str

class AnalysisResponse(BaseModel):
    score: float
    label: str
    confidence: float
    evidence: List[dict]
    explanation: str
    report_id: str
    timestamp: str
    breakdown: Optional[dict] = None  # Added breakdown

# Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "RealityFix API - Improved",
        "version": "2.0.0",
        "improvements": [
            "Enhanced domain trust scoring",
            "Advanced linguistic pattern analysis",
            "Multi-signal ensemble approach",
            "Better known source detection",
            "Transparent scoring breakdown"
        ],
        "endpoints": {
            "text_analysis": "/analyze/text",
            "image_analysis": "/analyze/image",
            "audio_analysis": "/analyze/audio",
            "report": "/report/{id}"
        }
    }

@app.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text content with IMPROVED accuracy
    
    Enhancements:
    - Domain trust database with 100+ sources
    - Advanced linguistic pattern detection
    - Multi-signal scoring (domain + content + structure)
    - Better handling of trusted vs unknown sources
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text too short for analysis (minimum 10 characters)")
        
        # Log analysis
        if request.url:
            print(f"Analyzing content from: {request.url}")
        
        # Perform IMPROVED analysis
        analysis_result = await text_detector.analyze(request.text, url=request.url)
        
        # Retrieve evidence from trusted sources
        evidence = await evidence_retriever.search(request.text[:200])
        
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Prepare response with breakdown
        response = AnalysisResponse(
            score=analysis_result['score'],
            label=analysis_result['label'],
            confidence=analysis_result['confidence'],
            evidence=evidence,
            explanation=analysis_result['explanation'],
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat(),
            breakdown=analysis_result.get('breakdown')  # Include scoring breakdown
        )
        
        # Save to database
        await database.save_report(
            report_id=report_id,
            content_type='text',
            content=request.text[:500],
            result=response.dict()
        )
        
        return response
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.post("/analyze/image", response_model=AnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """Analyze image for AI generation or manipulation"""
    try:
        if not request.image_url:
            raise HTTPException(status_code=400, detail="Image URL required")
        
        analysis_result = await image_detector.analyze(request.image_url)
        report_id = str(uuid.uuid4())
        
        response = AnalysisResponse(
            score=analysis_result['score'],
            label=analysis_result['label'],
            confidence=analysis_result['confidence'],
            evidence=[],
            explanation=analysis_result['explanation'],
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        await database.save_report(
            report_id=report_id,
            content_type='image',
            content=request.image_url,
            result=response.dict()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@app.post("/analyze/audio", response_model=AnalysisResponse)
async def analyze_audio(request: AudioAnalysisRequest):
    """Analyze audio for deepfake detection"""
    try:
        if not request.audio_url:
            raise HTTPException(status_code=400, detail="Audio URL required")
        
        analysis_result = await audio_detector.analyze(request.audio_url)
        report_id = str(uuid.uuid4())
        
        response = AnalysisResponse(
            score=analysis_result['score'],
            label=analysis_result['label'],
            confidence=analysis_result['confidence'],
            evidence=[],
            explanation=analysis_result['explanation'],
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        await database.save_report(
            report_id=report_id,
            content_type='audio',
            content=request.audio_url,
            result=response.dict()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio analysis failed: {str(e)}")

@app.get("/report/{report_id}")
async def get_report(report_id: str):
    """Retrieve full analysis report by ID"""
    try:
        report = await database.get_report(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return JSONResponse(content=report)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")

@app.get("/health")
async def health_check():
    """System health check with version info"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "models": {
            "text_detector": text_detector.is_loaded(),
            "image_detector": image_detector.is_loaded(),
            "audio_detector": audio_detector.is_loaded()
        },
        "database": await database.health_check(),
        "improvements": "Enhanced accuracy with multi-signal analysis"
    }

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "trusted_domains": len(text_detector.TRUSTED_DOMAINS),
        "unreliable_domains": len(text_detector.UNRELIABLE_DOMAINS),
        "red_flag_patterns": len(text_detector.STRONG_RED_FLAGS),
        "credibility_signals": len(text_detector.CREDIBILITY_SIGNALS),
        "analysis_components": [
            "Domain Trust Scoring",
            "Linguistic Pattern Analysis",
            "ML Model Analysis",
            "Metadata Analysis",
            "Ensemble Scoring"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("RealityFix API - Improved Version 2.0")
    print("=" * 50)
    print("Enhancements:")
    print("✓ 100+ trusted domain scores")
    print("✓ Advanced linguistic analysis")
    print("✓ Multi-signal ensemble approach")
    print("✓ Better misinformation detection")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)