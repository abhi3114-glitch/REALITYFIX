"""
Google Fact Check Tools API Integration
Free API for checking against verified fact-check databases
"""

import logging
import requests
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class FactChecker:
    """Check claims against Google's Fact Check database"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_FACTCHECK_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            logger.info("Fact Check API initialized")
        else:
            logger.info("Fact Check API key not found - fact-checking disabled")
    
    def is_available(self) -> bool:
        """Check if API is configured"""
        return self.enabled
    
    def check_claims(self, text: str, url: Optional[str] = None) -> Optional[Dict]:
        """
        Search for fact-checks related to the text
        
        Returns:
            Dict with:
                - found_checks: List of related fact-checks
                - debunked_claims: Number of claims that have been debunked
                - verified_claims: Number of verified claims
                - warnings: List of specific warnings
        """
        if not self.is_available():
            return None
        
        try:
            # Extract key phrases for searching (simple approach)
            search_query = self._extract_search_terms(text)
            
            params = {
                'key': self.api_key,
                'query': search_query,
                'languageCode': 'en',
                'pageSize': 5  # Get top 5 results
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_results(data)
            else:
                logger.warning(f"Fact Check API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Fact checker error: {e}")
            return None
    
    def _extract_search_terms(self, text: str) -> str:
        """Extract key terms for fact-check search"""
        # Take first ~300 chars or first few sentences
        if len(text) > 300:
            # Try to break at sentence
            cutoff = text[:300].rfind('.')
            if cutoff > 100:
                return text[:cutoff+1]
        return text[:300]
    
    def _process_results(self, data: Dict) -> Dict:
        """Process fact-check API results"""
        claims = data.get('claims', [])
        
        found_checks = []
        debunked_count = 0
        verified_count = 0
        warnings = []
        
        for claim in claims:
            claim_text = claim.get('text', '')
            claim_reviews = claim.get('claimReview', [])
            
            for review in claim_reviews:
                rating = review.get('textualRating', '').lower()
                publisher = review.get('publisher', {}).get('name', 'Unknown')
                url = review.get('url', '')
                
                check_info = {
                    'claim': claim_text,
                    'rating': review.get('textualRating', 'Unknown'),
                    'publisher': publisher,
                    'url': url
                }
                found_checks.append(check_info)
                
                # Count debunked vs verified
                if any(word in rating for word in ['false', 'misleading', 'pants on fire', 'incorrect']):
                    debunked_count += 1
                    warnings.append(f"Claim '{claim_text[:50]}...' rated as {rating} by {publisher}")
                elif any(word in rating for word in ['true', 'correct', 'accurate']):
                    verified_count += 1
        
        return {
            'found_checks': found_checks,
            'debunked_claims': debunked_count,
            'verified_claims': verified_count,
            'warnings': warnings,
            'total_checks': len(found_checks)
        }

# Global instance
fact_checker = FactChecker()
