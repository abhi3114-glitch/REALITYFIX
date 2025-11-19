"""
FastAPI Backend - Main Application
Handles all API routes for text, image, and audio analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

from text_detector import TextDetector
from image_detector import ImageDetector
from audio_detector import AudioDetector
from evidence_retriever import EvidenceRetriever
from database import Database

# Initialize FastAPI app
app = FastAPI(
    title="RealityFix API",
    description="Real-time fake news and manipulated media detection API",
    version="1.0.0"
)

# CORS middleware for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
text_detector = TextDetector()
image_detector = ImageDetector()
audio_detector = AudioDetector()
evidence_retriever = EvidenceRetriever()
database = Database()

# Request/Response Models
class TextAnalysisRequest(BaseModel):
    text: str

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

# Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "RealityFix API",
        "version": "1.0.0",
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
    Analyze text content for misinformation
    
    Args:
        request: TextAnalysisRequest with text field
        
    Returns:
        AnalysisResponse with score, label, confidence, evidence, and report_id
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text too short for analysis")
        
        # Perform text analysis
        analysis_result = await text_detector.analyze(request.text)
        
        # Retrieve evidence from trusted sources
        evidence = await evidence_retriever.search(request.text[:200])
        
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Prepare response
        response = AnalysisResponse(
            score=analysis_result['score'],
            label=analysis_result['label'],
            confidence=analysis_result['confidence'],
            evidence=evidence,
            explanation=analysis_result['explanation'],
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat()
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
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.post("/analyze/image", response_model=AnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze image for AI generation or manipulation
    
    Args:
        request: ImageAnalysisRequest with image_url field
        
    Returns:
        AnalysisResponse with score, label, confidence, and report_id
    """
    try:
        # Validate input
        if not request.image_url:
            raise HTTPException(status_code=400, detail="Image URL required")
        
        # Perform image analysis
        analysis_result = await image_detector.analyze(request.image_url)
        
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Prepare response
        response = AnalysisResponse(
            score=analysis_result['score'],
            label=analysis_result['label'],
            confidence=analysis_result['confidence'],
            evidence=[],  # Image analysis doesn't use text evidence
            explanation=analysis_result['explanation'],
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save to database
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
    """
    Analyze audio for deepfake detection
    
    Args:
        request: AudioAnalysisRequest with audio_url field
        
    Returns:
        AnalysisResponse with score, label, confidence, and report_id
    """
    try:
        # Validate input
        if not request.audio_url:
            raise HTTPException(status_code=400, detail="Audio URL required")
        
        # Perform audio analysis
        analysis_result = await audio_detector.analyze(request.audio_url)
        
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Prepare response
        response = AnalysisResponse(
            score=analysis_result['score'],
            label=analysis_result['label'],
            confidence=analysis_result['confidence'],
            evidence=[],  # Audio analysis doesn't use text evidence
            explanation=analysis_result['explanation'],
            report_id=report_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save to database
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
    """
    Retrieve full analysis report by ID
    
    Args:
        report_id: UUID of the report
        
    Returns:
        Full report with all analysis details
    """
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
    """System health check"""
    return {
        "status": "healthy",
        "models": {
            "text_detector": text_detector.is_loaded(),
            "image_detector": image_detector.is_loaded(),
            "audio_detector": audio_detector.is_loaded()
        },
        "database": await database.health_check()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)