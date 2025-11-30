"""
Google Gemini API Integration for Advanced Text Analysis
Uses Gemini 1.5 Flash (free tier) for deep content verification
"""

import os
import json
import logging
from typing import Dict, Optional, List
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Analyze text using Google Gemini API for advanced fact-checking"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.enabled = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Try gemini-1.5-flash
                self.model = genai.GenerativeModel('models/gemini-1.5-flash')
                self.enabled = True
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {e}")
        else:
            logger.info("Gemini API key not found - LLM analysis disabled")
    
    def is_available(self) -> bool:
        """Check if Gemini API is configured and available"""
        return self.enabled and self.model is not None
    
    async def analyze_credibility(self, text: str, url: Optional[str] = None) -> Optional[Dict]:
        """
        Use Gemini to analyze text credibility with advanced reasoning
        
        Returns:
            Dict with:
                - credibility_score: 0-1 float
                - claims: List of factual claims found
                - red_flags: List of problematic patterns
                - reasoning: Explanation of the analysis
                - bias_detected: Political/commercial bias if any
        """
        if not self.is_available():
            return None
        
        try:
            prompt = self._build_analysis_prompt(text, url)
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,  # Low temp for consistency
                    'top_p': 0.8,
                    'max_output_tokens': 1024,
                }
            )
            
            # Parse structured response
            result = self._parse_response(response.text)
            return result
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    def _build_analysis_prompt(self, text: str, url: Optional[str]) -> str:
        """Build structured prompt for credibility analysis"""
        
        # Truncate text if too long (stay within token limits)
        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        url_context = f"\nSource URL: {url}" if url else ""
        
        prompt = f"""You are an expert fact-checker and misinformation analyst. Analyze this article for credibility and potential misinformation.
{url_context}

ARTICLE TEXT:
{text}

Provide your analysis in the following JSON format:
{{
    "credibility_score": <float 0-1, where 1=highly credible, 0=likely false>,
    "claims": [<list of main factual claims made in the article>],
    "red_flags": [<list of concerning patterns: clickbait, emotional manipulation, unsourced claims, logical fallacies, etc.>],
    "reasoning": "<concise explanation of your credibility assessment>",
    "bias_detected": "<political/commercial bias if present, or 'none'>",
    "verification_needed": [<specific claims that should be fact-checked>]
}}

Focus on:
1. Verifiable facts vs. opinions/speculation
2. Source citations and evidence quality
3. Logical consistency and reasoning
4. Emotional manipulation tactics
5. Clickbait or sensationalist language
6. Missing context or cherry-picked data

Return ONLY the JSON, no other text."""

        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini's JSON response"""
        try:
            # Extract JSON from response (in case there's extra text)
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start:end]
            result = json.loads(json_str)
            
            # Validate required fields
            required = ['credibility_score', 'claims', 'red_flags', 'reasoning']
            for field in required:
                if field not in result:
                    logger.warning(f"Missing field in Gemini response: {field}")
                    result[field] = self._get_default_value(field)
            
            # Ensure score is in valid range
            result['credibility_score'] = max(0.0, min(1.0, float(result['credibility_score'])))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            # Return safe default
            return {
                'credibility_score': 0.5,
                'claims': [],
                'red_flags': ['Analysis parsing failed'],
                'reasoning': 'Could not parse AI analysis',
                'bias_detected': 'unknown'
            }
    
    def _get_default_value(self, field: str):
        """Get default value for missing fields"""
        defaults = {
            'credibility_score': 0.5,
            'claims': [],
            'red_flags': [],
            'reasoning': 'Analysis incomplete',
            'bias_detected': 'unknown',
            'verification_needed': []
        }
        return defaults.get(field, None)

# Global instance
gemini_analyzer = GeminiAnalyzer()
