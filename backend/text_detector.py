"""
Text Detector - Analyzes text content for misinformation
Uses pretrained transformer models for classification
"""

import torch
import numpy as np
from typing import Dict
import logging
from model_loader import model_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextDetector:
    """Detects misinformation in text content"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load pretrained text classification model"""
        try:
            self.model, self.tokenizer = model_loader.load_text_model()
            logger.info("Text detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize text detector: {e}")
            self.model = None
            self.tokenizer = None
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None
    
    async def analyze(self, text: str) -> Dict:
        """
        Analyze text for misinformation
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with score, label, confidence, and explanation
        """
        try:
            if not self.is_loaded():
                logger.warning("Model not loaded, using fallback analysis")
                return self._fallback_analysis(text)
            
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move to device
            device = model_loader.get_device()
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # Extract scores
            probs = probabilities[0].cpu().numpy()
            
            # Calculate trust score (0-1 scale)
            # Higher score = more trustworthy
            trust_score = float(probs[1]) if len(probs) > 1 else 0.5
            
            # Determine label
            if trust_score >= 0.7:
                label = "trustworthy"
            elif trust_score >= 0.4:
                label = "suspicious"
            else:
                label = "misinformation"
            
            # Calculate confidence
            confidence = float(max(probs))
            
            # Generate explanation
            explanation = self._generate_explanation(text, trust_score, label)
            
            return {
                'score': trust_score,
                'label': label,
                'confidence': confidence,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error(f"Text analysis error: {e}")
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text: str) -> Dict:
        """
        Fallback analysis when model is not available
        Uses simple heuristics
        """
        # Simple heuristic-based analysis
        suspicious_keywords = [
            'shocking', 'unbelievable', 'miracle', 'secret', 'they don\'t want you to know',
            'click here', 'breaking', 'exclusive', 'leaked', 'conspiracy'
        ]
        
        text_lower = text.lower()
        suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in text_lower)
        
        # Calculate score based on suspicious keywords
        score = max(0.3, 0.8 - (suspicious_count * 0.1))
        
        if score >= 0.7:
            label = "trustworthy"
        elif score >= 0.4:
            label = "suspicious"
        else:
            label = "misinformation"
        
        return {
            'score': score,
            'label': label,
            'confidence': 0.6,
            'explanation': f"Heuristic analysis detected {suspicious_count} suspicious indicators."
        }
    
    def _generate_explanation(self, text: str, score: float, label: str) -> str:
        """Generate human-readable explanation"""
        if label == "trustworthy":
            return f"The text appears credible with a trust score of {score:.2f}. Language patterns and content structure suggest reliable information."
        elif label == "suspicious":
            return f"The text shows mixed signals with a trust score of {score:.2f}. Some content patterns warrant additional verification."
        else:
            return f"The text shows signs of misinformation with a low trust score of {score:.2f}. Multiple red flags detected in language patterns and claims."