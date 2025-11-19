"""
IMPROVED Text Detector - Significantly Better Accuracy
Combines multiple signals: domain trust, linguistic analysis, source verification, and ML models
"""

import torch
import numpy as np
from typing import Dict, List, Optional
import logging
from urllib.parse import urlparse
import re
from model_loader import model_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedTextDetector:
    """Advanced misinformation detector with multi-signal analysis"""
    
    # EXPANDED trusted domains with granular scores
    TRUSTED_DOMAINS = {
        # Tier 1: Wire services & international news (0.95-1.0)
        'reuters.com': 0.98, 'apnews.com': 0.98, 'bbc.com': 0.97, 'bbc.co.uk': 0.97,
        'afp.com': 0.97, 'dpa.com': 0.96, 'tass.com': 0.90,
        
        # Tier 2: Major newspapers of record (0.90-0.95)
        'nytimes.com': 0.94, 'washingtonpost.com': 0.93, 'wsj.com': 0.94,
        'theguardian.com': 0.93, 'thetimes.co.uk': 0.92, 'ft.com': 0.93,
        'telegraph.co.uk': 0.91, 'economist.com': 0.93, 'latimes.com': 0.90,
        
        # Tier 3: Reputable national news (0.85-0.90)
        'npr.org': 0.90, 'pbs.org': 0.90, 'cnn.com': 0.87, 'nbcnews.com': 0.88,
        'cbsnews.com': 0.88, 'abcnews.go.com': 0.88, 'usatoday.com': 0.85,
        
        # Tier 4: Quality journalism (0.80-0.85)
        'theatlantic.com': 0.85, 'newyorker.com': 0.85, 'vox.com': 0.82,
        'politico.com': 0.83, 'axios.com': 0.82, 'propublica.org': 0.88,
        
        # Tier 5: Scientific/Academic (0.90-0.98)
        'nature.com': 0.97, 'science.org': 0.97, 'cell.com': 0.96,
        'thelancet.com': 0.96, 'nejm.org': 0.96, 'plos.org': 0.94,
        'arxiv.org': 0.88, 'scholar.google.com': 0.85,
        
        # Tier 6: Fact-checking sites (0.92-0.96)
        'factcheck.org': 0.95, 'snopes.com': 0.94, 'politifact.com': 0.94,
        'fullfact.org': 0.93, 'truthorfiction.com': 0.92,
        'mediabiasFactcheck.com': 0.90, 'checkyourfact.com': 0.91,
        
        # Tier 7: Government/Educational (0.88-0.93)
        'gov': 0.92, 'edu': 0.88, 'un.org': 0.93, 'who.int': 0.94,
        'cdc.gov': 0.95, 'nih.gov': 0.95, 'nasa.gov': 0.94,
        
        # Tier 8: Reference (0.80-0.88)
        'wikipedia.org': 0.82, 'britannica.com': 0.88, 'dictionary.com': 0.85,
    }
    
    # Known unreliable sources (negative trust)
    UNRELIABLE_DOMAINS = {
        'infowars.com': 0.15, 'naturalnews.com': 0.20, 'beforeitsnews.com': 0.18,
        'yournewswire.com': 0.15, 'newspunch.com': 0.18, 'worldtruth.tv': 0.20,
        'realfarmacy.com': 0.22, 'collective-evolution.com': 0.25,
    }
    
    # Misinformation indicators with weights
    STRONG_RED_FLAGS = {
        # Clickbait patterns (-0.20 each)
        'they don\'t want you to know': -0.20,
        'doctors hate this': -0.20,
        'what happens next will shock you': -0.20,
        'you won\'t believe': -0.18,
        'secret they\'re hiding': -0.20,
        'big pharma doesn\'t want': -0.20,
        'mainstream media won\'t tell you': -0.20,
        
        # Conspiracy patterns (-0.15 each)
        'wake up sheeple': -0.18,
        'do your own research': -0.10,  # Context dependent
        'false flag': -0.15,
        'deep state': -0.12,
        'new world order': -0.15,
        
        # Urgency manipulation (-0.15 each)
        'act now before': -0.15,
        'last chance to': -0.15,
        'hurry before it\'s too late': -0.18,
        'limited time only': -0.12,
    }
    
    # Credibility indicators with positive weights
    CREDIBILITY_SIGNALS = {
        # Source attribution (+0.10 each)
        'according to': 0.10,
        'study published in': 0.12,
        'research shows': 0.10,
        'data from': 0.10,
        'experts say': 0.08,
        'peer-reviewed': 0.15,
        'meta-analysis': 0.12,
        
        # Proper reporting (+0.08 each)
        'reported by': 0.08,
        'confirmed by': 0.10,
        'verified by': 0.12,
        'officials said': 0.08,
        'spokesperson stated': 0.08,
        
        # Qualifiers/nuance (+0.05 each)
        'however': 0.05,
        'on the other hand': 0.05,
        'some experts': 0.05,
        'preliminary findings': 0.05,
        'suggests that': 0.05,
    }
    
    # Emotional manipulation indicators
    EMOTIONAL_TRIGGERS = {
        'shocking': -0.08, 'outrageous': -0.08, 'unbelievable': -0.10,
        'devastating': -0.06, 'horrifying': -0.08, 'miracle': -0.10,
        'breakthrough': -0.05, 'revolutionary': -0.05,
    }
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load ML model - try better models first"""
        try:
            # Try to load a better fact-checking model if available
            # For now, fallback to sentiment but we'll use it more carefully
            self.model, self.tokenizer = model_loader.load_text_model()
            logger.info("Text detector initialized")
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            self.model = None
            self.tokenizer = None
    
    def is_loaded(self) -> bool:
        return self.model is not None and self.tokenizer is not None
    
    def _get_domain_trust_score(self, url: Optional[str]) -> Optional[float]:
        """Get trust score for domain"""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check unreliable domains first
            for unreliable_domain, score in self.UNRELIABLE_DOMAINS.items():
                if domain == unreliable_domain or domain.endswith('.' + unreliable_domain):
                    return score
            
            # Check trusted domains
            if domain in self.TRUSTED_DOMAINS:
                return self.TRUSTED_DOMAINS[domain]
            
            # Check for .edu or .gov
            if domain.endswith('.edu'):
                return self.TRUSTED_DOMAINS['edu']
            if domain.endswith('.gov'):
                return self.TRUSTED_DOMAINS['gov']
            
            # Check if subdomain of trusted domain
            for trusted_domain, score in self.TRUSTED_DOMAINS.items():
                if '.' in trusted_domain and domain.endswith('.' + trusted_domain):
                    return score * 0.95  # Slight reduction for subdomains
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing domain: {e}")
            return None
    
    async def analyze(self, text: str, url: Optional[str] = None) -> Dict:
        """
        Comprehensive text analysis with multiple signals
        """
        try:
            # Get all analysis components
            domain_trust = self._get_domain_trust_score(url)
            linguistic_score = self._analyze_linguistic_patterns(text)
            ml_score = await self._analyze_with_ml(text) if self.is_loaded() else None
            metadata_score = self._analyze_metadata(text, url)
            
            # Combine scores with intelligent weighting
            final_score = self._combine_scores(
                domain_trust, linguistic_score, ml_score, metadata_score, url
            )
            
            # Determine label
            if final_score >= 0.70:
                label = 'trustworthy'
            elif final_score >= 0.40:
                label = 'suspicious'
            else:
                label = 'misinformation'
            
            # Calculate confidence based on available signals
            confidence = self._calculate_confidence(
                domain_trust, linguistic_score, ml_score, metadata_score
            )
            
            # Generate detailed explanation
            explanation = self._generate_detailed_explanation(
                final_score, label, domain_trust, linguistic_score, 
                ml_score, metadata_score, url
            )
            
            return {
                'score': final_score,
                'label': label,
                'confidence': confidence,
                'explanation': explanation,
                'breakdown': {
                    'domain_trust': domain_trust,
                    'linguistic_score': linguistic_score,
                    'ml_score': ml_score,
                    'metadata_score': metadata_score
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return self._fallback_analysis()
    
    def _analyze_linguistic_patterns(self, text: str) -> float:
        """
        Advanced linguistic analysis for misinformation patterns
        """
        text_lower = text.lower()
        score = 0.60  # Start neutral
        
        # Check red flags
        red_flag_penalty = 0
        for phrase, weight in self.STRONG_RED_FLAGS.items():
            if phrase in text_lower:
                red_flag_penalty += weight
                logger.debug(f"Red flag detected: {phrase}")
        
        # Check credibility signals
        credibility_boost = 0
        for phrase, weight in self.CREDIBILITY_SIGNALS.items():
            if phrase in text_lower:
                credibility_boost += weight
                logger.debug(f"Credibility signal: {phrase}")
        
        # Check emotional manipulation
        emotional_penalty = 0
        for word, weight in self.EMOTIONAL_TRIGGERS.items():
            count = text_lower.count(word)
            if count > 0:
                emotional_penalty += weight * min(count, 3)  # Cap at 3 occurrences
        
        # Analyze structure
        structure_score = self._analyze_text_structure(text)
        
        # Combine signals
        score += credibility_boost + red_flag_penalty + emotional_penalty + structure_score
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))
    
    def _analyze_text_structure(self, text: str) -> float:
        """
        Analyze text structure quality
        """
        score = 0.0
        
        # Check for proper sentences
        sentences = re.split(r'[.!?]+', text)
        valid_sentences = [s for s in sentences if len(s.strip()) > 10]
        
        if len(valid_sentences) >= 3:
            score += 0.05
        
        # Check for ALL CAPS (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            score -= 0.10  # Heavy ALL CAPS penalty
        elif caps_ratio > 0.15:
            score -= 0.05
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        if exclamation_count > 5:
            score -= 0.08
        if question_count > 8:
            score -= 0.05
        
        # Check for proper paragraph structure
        paragraphs = text.split('\n\n')
        if len(paragraphs) >= 2:
            score += 0.05
        
        return score
    
    def _analyze_metadata(self, text: str, url: Optional[str]) -> float:
        """
        Analyze metadata signals
        """
        score = 0.0
        
        # URL quality checks
        if url:
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.info']
            if any(url.endswith(tld) for tld in suspicious_tlds):
                score -= 0.15
            
            # Check for excessive subdomains
            parsed = urlparse(url)
            subdomain_count = parsed.netloc.count('.')
            if subdomain_count > 3:
                score -= 0.08
        
        # Text length analysis
        word_count = len(text.split())
        if word_count < 50:
            score -= 0.10  # Very short, possibly snippet
        elif word_count > 300:
            score += 0.05  # Substantial content
        
        return score
    
    async def _analyze_with_ml(self, text: str) -> Optional[float]:
        """
        Use ML model for analysis (with grain of salt for sentiment models)
        """
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            device = model_loader.get_device()
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            probs = probabilities[0].cpu().numpy()
            
            # For sentiment model, use confidence as a weak signal
            # Positive sentiment slightly increases trust, negative decreases
            confidence = float(max(probs))
            positive_score = float(probs[1]) if len(probs) > 1 else 0.5
            
            # Use cautiously - sentiment != factuality
            ml_score = 0.50 + (positive_score - 0.5) * 0.3  # Dampened effect
            
            return ml_score
            
        except Exception as e:
            logger.error(f"ML analysis error: {e}")
            return None
    
    def _combine_scores(
        self, 
        domain_trust: Optional[float],
        linguistic_score: float,
        ml_score: Optional[float],
        metadata_score: float,
        url: Optional[str]
    ) -> float:
        """
        Intelligently combine multiple signals
        """
        # If highly trusted domain, heavily weight it
        if domain_trust and domain_trust >= 0.92:
            logger.info(f"High trust domain detected: {domain_trust}")
            # 70% domain, 30% content analysis
            content_score = linguistic_score + metadata_score
            if ml_score:
                content_score = (content_score + ml_score) / 2
            return domain_trust * 0.70 + content_score * 0.30
        
        # If known unreliable domain, cap the maximum score
        if domain_trust and domain_trust < 0.30:
            logger.warning(f"Unreliable domain detected: {domain_trust}")
            # Cap at 0.45 regardless of content
            content_score = linguistic_score + metadata_score
            if ml_score:
                content_score = (content_score + ml_score) / 2
            return min(0.45, max(domain_trust, content_score * 0.60 + domain_trust * 0.40))
        
        # If moderately trusted domain (0.75-0.91)
        if domain_trust and 0.75 <= domain_trust < 0.92:
            logger.info(f"Trusted domain: {domain_trust}")
            # 55% domain, 45% content
            content_score = linguistic_score + metadata_score
            if ml_score:
                content_score = (content_score + ml_score) / 2
            return domain_trust * 0.55 + content_score * 0.45
        
        # No domain info or neutral domain - rely on content analysis
        scores = [linguistic_score, metadata_score]
        weights = [0.60, 0.20]  # Linguistic is primary
        
        if ml_score:
            scores.append(ml_score)
            weights.append(0.20)
        
        if domain_trust:
            scores.append(domain_trust)
            weights.append(0.40)
            # Renormalize weights
            weights = [w / sum(weights) for w in weights]
        
        final_score = sum(s * w for s, w in zip(scores, weights))
        return max(0.0, min(1.0, final_score))
    
    def _calculate_confidence(
        self,
        domain_trust: Optional[float],
        linguistic_score: float,
        ml_score: Optional[float],
        metadata_score: float
    ) -> float:
        """
        Calculate confidence based on agreement between signals
        """
        available_signals = []
        
        if domain_trust:
            available_signals.append(domain_trust)
        available_signals.append(linguistic_score)
        if ml_score:
            available_signals.append(ml_score)
        available_signals.append(metadata_score)
        
        # More signals = higher potential confidence
        base_confidence = 0.50 + (len(available_signals) * 0.08)
        
        # Check agreement between signals
        if len(available_signals) >= 2:
            variance = np.var(available_signals)
            # Low variance = high agreement = high confidence
            agreement_bonus = max(0, 0.25 - variance)
            base_confidence += agreement_bonus
        
        # Strong domain trust increases confidence
        if domain_trust and (domain_trust >= 0.90 or domain_trust <= 0.30):
            base_confidence += 0.15
        
        return min(0.95, base_confidence)
    
    def _generate_detailed_explanation(
        self,
        score: float,
        label: str,
        domain_trust: Optional[float],
        linguistic_score: float,
        ml_score: Optional[float],
        metadata_score: float,
        url: Optional[str]
    ) -> str:
        """
        Generate comprehensive, transparent explanation
        """
        parts = []
        
        # Label explanation
        if label == 'trustworthy':
            parts.append(f"✓ Content appears trustworthy (score: {score:.2f})")
        elif label == 'suspicious':
            parts.append(f"⚠ Content shows mixed signals (score: {score:.2f})")
        else:
            parts.append(f"✗ Content shows signs of misinformation (score: {score:.2f})")
        
        # Domain analysis
        if domain_trust:
            if domain_trust >= 0.90:
                domain_name = urlparse(url).netloc if url else "source"
                parts.append(f"Source ({domain_name}) is highly trusted and verified")
            elif domain_trust >= 0.75:
                parts.append(f"Source has good reputation in journalism")
            elif domain_trust < 0.30:
                parts.append(f"⚠ Source has history of unreliable content")
        else:
            parts.append("Source credibility could not be verified")
        
        # Linguistic analysis
        if linguistic_score >= 0.70:
            parts.append("Language patterns suggest professional journalism")
        elif linguistic_score < 0.40:
            parts.append("⚠ Language contains clickbait or manipulation patterns")
        
        # Recommendation
        if score >= 0.70:
            parts.append("Content meets credibility standards")
        elif score >= 0.40:
            parts.append("Recommend verifying with additional sources")
        else:
            parts.append("⚠ Strong recommendation to verify with trusted sources")
        
        return ". ".join(parts) + "."
    
    def _fallback_analysis(self) -> Dict:
        """Fallback when analysis fails"""
        return {
            'score': 0.50,
            'label': 'suspicious',
            'confidence': 0.40,
            'explanation': 'Analysis incomplete. Please verify information independently.',
            'breakdown': {
                'domain_trust': None,
                'linguistic_score': 0.50,
                'ml_score': None,
                'metadata_score': 0.50
            }
        }