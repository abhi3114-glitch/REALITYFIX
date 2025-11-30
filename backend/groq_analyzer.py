"""
Groq API Analyzer for RealityFix
Uses Llama 3.3 via Groq's ultra-fast API for credibility analysis
"""

import os
import json
import logging
from typing import Dict, Optional, List
from groq import Groq

logger = logging.getLogger(__name__)

class GroqAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        
        # Fallback: Try to read from .env manually if not found
        if not self.api_key:
            try:
                env_path = os.path.join(os.path.dirname(__file__), '.env')
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.strip().startswith('GROQ_API_KEY='):
                                self.api_key = line.strip().split('=', 1)[1].strip()
                                logger.info("Loaded GROQ_API_KEY from .env manually")
                                break
            except Exception as e:
                logger.warning(f"Manual .env load failed: {e}")

        self.client = None
        self.model = "llama-3.3-70b-versatile"  # High performance model
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"Groq API initialized with model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq API: {e}")
        else:
            logger.warning("GROQ_API_KEY not found in environment variables")

    def is_available(self) -> bool:
        return self.client is not None

    async def analyze_credibility(self, text: str, url: Optional[str] = None) -> Optional[Dict]:
        """
        Analyze text credibility using Groq (Llama 3.3)
        """
        if not self.is_available():
            return None

        try:
            prompt = self._build_prompt(text, url)
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert fact-checker and media literacy analyst. Analyze the given text for credibility, bias, and factual accuracy. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            return self._parse_response(response_text)
            
        except Exception as e:
            logger.error(f"Groq analysis failed: {e}")
            return None

    def _build_prompt(self, text: str, url: Optional[str]) -> str:
        return f"""
        Analyze the following article text for credibility.
        
        URL: {url if url else 'Not provided'}
        TEXT: {text[:4000]}... (truncated)
        
        Provide a JSON response with this exact structure:
        {{
            "credibility_score": <float between 0.0 and 1.0>,
            "claims": ["<specific factual claim 1>", "<specific factual claim 2>"],
            "red_flags": ["<red flag 1>", "<red flag 2>"],
            "bias_detected": "<description of political/commercial bias or 'None'>",
            "reasoning": "<concise explanation of the score>"
        }}
        """

    def _parse_response(self, response_text: str) -> Optional[Dict]:
        try:
            # Clean up potential markdown code blocks
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Groq JSON response: {response_text[:100]}...")
            return None

# Singleton instance
groq_analyzer = GroqAnalyzer()
