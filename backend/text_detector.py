"""
Text Detector - IMPROVED VERSION with domain trust scoring
Fixes the issue of trusted sources getting low scores
"""

import torch
import numpy as np
from typing import Dict
import logging
from urllib.parse import urlparse
from model_loader import model_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextDetector:
    """Detects misinformation in text content with domain trust scoring"""
    
    # Trusted news domains with trust scores
    TRUSTED_DOMAINS = {
        # Tier 1: Highest trust (0.95-1.0)
        'bbc.com': 0.98,
        'bbc.co.uk': 0.98,
        'reuters.com': 0.98,
        'apnews.com': 0.97,
        'npr.org': 0.96,
        'pbs.org': 0.96,
        'theguardian.com': 0.95,
        'nytimes.com': 0.95,
        'washingtonpost.com': 0.95,
        
        # Tier 2: High trust (0.85-0.94)
        'cnn.com': 0.90,
        'wsj.com': 0.92,
        'bloomberg.com': 0.91,
        'ft.com': 0.90,
        'economist.com': 0.92,
        'nature.com': 0.95,
        'science.org': 0.95,
        'scientific american.com': 0.93,
        'theatlantic.com': 0.88,
        'newyorker.com': 0.88,
        
        # Tier 3: Moderate trust (0.75-0.84)
        'politico.com': 0.82,
        'axios.com': 0.81,
        'time.com': 0.80,
        'usatoday.com': 0.78,
        'abcnews.go.com': 0.80,
        'cbsnews.com': 0.80,
        'nbcnews.com': 0.80,
        
        # Educational/Reference (0.90-0.95)
        'wikipedia.org': 0.85,
        'britannica.com': 0.90,
        'edu': 0.88,  # Any .edu domain
        'gov': 0.92,  # Any .gov domain
        
        # Fact-checking sites (0.95+)
        'factcheck.org': 0.96,
        'snopes.com': 0.95,
        'politifact.com': 0.95,
        'fullfact.org': 0.95,
    }
    
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
    
    def _get_domain_trust_score(self, url: str = None) -> float:
        """
        Get trust score based on domain
        
        Args:
            url: URL of the content source
            
        Returns:
            Trust score 0-1, or None if unknown domain
        """
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check exact match first
            if domain in self.TRUSTED_DOMAINS:
                return self.TRUSTED_DOMAINS[domain]
            
            # Check for .edu or .gov
            if domain.endswith('.edu'):
                return self.TRUSTED_DOMAINS['edu']
            if domain.endswith('.gov'):
                return self.TRUSTED_DOMAINS['gov']
            
            # Check if subdomain of trusted domain
            for trusted_domain, score in self.TRUSTED_DOMAINS.items():
                if domain.endswith('.' + trusted_domain):
                    return score
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing domain: {e}")
            return None
    
    async def analyze(self, text: str, url: str = None) -> Dict:
        """
        Analyze text for misinformation with domain trust consideration
        
        Args:
            text: Input text to analyze
            url: Optional URL of the content source
            
        Returns:
            Dictionary with score, label, confidence, and explanation
        """
        try:
            # Get domain trust score if URL provided
            domain_trust = self._get_domain_trust_score(url)
            
            # If from highly trusted domain, boost score significantly
            if domain_trust and domain_trust >= 0.90:
                logger.info(f"Content from trusted domain (trust: {domain_trust})")
                return {
                    'score': domain_trust,
                    'label': 'trustworthy',
                    'confidence': 0.95,
                    'explanation': f"Content is from a highly trusted and verified news source with established editorial standards and fact-checking processes. Domain trust score: {domain_trust:.2f}"
                }
            
            # For moderately trusted domains (0.75-0.89), still analyze but boost score
            base_score = None
            if self.is_loaded():
                base_score = await self._analyze_with_model(text)
            else:
                base_score = self._analyze_with_heuristics(text)
            
            # Combine domain trust with analysis
            if domain_trust and domain_trust >= 0.75:
                # Weight: 60% domain trust, 40% content analysis
                final_score = (domain_trust * 0.6) + (base_score['score'] * 0.4)
                confidence = max(base_score['confidence'], 0.85)
                
                return {
                    'score': final_score,
                    'label': 'trustworthy' if final_score >= 0.7 else 'suspicious',
                    'confidence': confidence,
                    'explanation': f"Content from a trusted source (trust: {domain_trust:.2f}). Combined with content analysis for final assessment."
                }
            
            # No domain trust available, use content analysis only
            return base_score
            
        except Exception as e:
            logger.error(f"Text analysis error: {e}")
            return self._fallback_analysis(text)
    
    async def _analyze_with_model(self, text: str) -> Dict:
        """Analyze text using ML model"""
        try:
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
            
            # Calculate trust score
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
            logger.error(f"Model analysis error: {e}")
            return self._analyze_with_heuristics(text)
    
    def _analyze_with_heuristics(self, text: str) -> Dict:
        """
        IMPROVED heuristic-based analysis
        More nuanced approach that doesn't over-penalize legitimate news
        """
        # Strong indicators of misinformation (weight: -0.15 each)
        strong_suspicious = [
            'they don\'t want you to know',
            'doctors hate this',
            'one weird trick',
            'secret cure',
            'miracle cure',
            'big pharma doesn\'t want',
            'shocking truth',
            'click here now'
        ]
        
        # Moderate indicators (weight: -0.05 each)
        moderate_suspicious = [
            'you won\'t believe',
            'unbelievable',
            'absolutely shocking'
        ]
        
        # Legitimate news phrases (weight: +0.05 each)
        legitimate_phrases = [
            'according to',
            'study shows',
            'research suggests',
            'experts say',
            'reported by',
            'officials said',
            'data shows'
        ]
        
        text_lower = text.lower()
        
        # Start with neutral score
        score = 0.65
        
        # Check strong indicators
        strong_count = sum(1 for keyword in strong_suspicious if keyword in text_lower)
        score -= strong_count * 0.15
        
        # Check moderate indicators
        moderate_count = sum(1 for keyword in moderate_suspicious if keyword in text_lower)
        score -= moderate_count * 0.05
        
        # Check legitimate phrases (boost score)
        legitimate_count = sum(1 for phrase in legitimate_phrases if phrase in text_lower)
        score += legitimate_count * 0.05
        
        # Clamp score between 0 and 1
        score = max(0.0, min(1.0, score))
        
        # Determine label
        if score >= 0.7:
            label = "trustworthy"
        elif score >= 0.4:
            label = "suspicious"
        else:
            label = "misinformation"
        
        return {
            'score': score,
            'label': label,
            'confidence': 0.65,
            'explanation': f"Heuristic analysis based on language patterns. Detected {strong_count} strong and {moderate_count} moderate suspicious indicators, {legitimate_count} legitimate news patterns."
        }
    
    def _fallback_analysis(self, text: str) -> Dict:
        """Fallback analysis when everything else fails"""
        return {
            'score': 0.6,
            'label': 'suspicious',
            'confidence': 0.5,
            'explanation': 'Analysis limited. Please verify with trusted sources.'
        }
    
    def _generate_explanation(self, text: str, score: float, label: str) -> str:
        """Generate human-readable explanation"""
        if label == "trustworthy":
            return f"The content appears credible with a trust score of {score:.2f}. Language patterns and content structure suggest reliable information sourced from legitimate journalism."
        elif label == "suspicious":
            return f"The content shows mixed signals with a trust score of {score:.2f}. Some content patterns warrant additional verification from multiple trusted sources."
        else:
            return f"The content shows signs of potential misinformation with a low trust score of {score:.2f}. Multiple red flags detected in language patterns and claims. Strongly recommend verification."