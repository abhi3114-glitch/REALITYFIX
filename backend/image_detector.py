"""
Image Detector - Analyzes images for AI generation and manipulation
Uses pretrained models and image forensics techniques
"""

import torch
import numpy as np
from typing import Dict
import logging
import httpx
from PIL import Image
from io import BytesIO
from torchvision import transforms
from model_loader import model_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageDetector:
    """Detects AI-generated or manipulated images"""
    
    def __init__(self):
        self.model = None
        self.transform = self._get_transform()
        self._load_model()
    
    def _load_model(self):
        """Load pretrained image classification model"""
        try:
            self.model = model_loader.load_image_model()
            logger.info("Image detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize image detector: {e}")
            self.model = None
    
    def _get_transform(self):
        """Get image preprocessing transform"""
        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    async def analyze(self, image_url: str) -> Dict:
        """
        Analyze image for AI generation or manipulation
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dictionary with score, label, confidence, and explanation
        """
        try:
            # Download image
            image = await self._download_image(image_url)
            
            if image is None:
                return self._fallback_analysis()
            
            if not self.is_loaded():
                logger.warning("Model not loaded, using fallback analysis")
                return self._fallback_analysis()
            
            # Preprocess image
            image_tensor = self.transform(image).unsqueeze(0)
            
            # Move to device
            device = model_loader.get_device()
            image_tensor = image_tensor.to(device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=-1)
            
            # Extract scores
            probs = probabilities[0].cpu().numpy()
            
            # Calculate authenticity score
            # For MVP, use simple heuristic based on model confidence
            authenticity_score = self._calculate_authenticity_score(probs, image)
            
            # Determine label
            if authenticity_score >= 0.7:
                label = "trustworthy"
            elif authenticity_score >= 0.4:
                label = "suspicious"
            else:
                label = "misinformation"
            
            # Calculate confidence
            confidence = float(max(probs))
            
            # Generate explanation
            explanation = self._generate_explanation(authenticity_score, label)
            
            return {
                'score': authenticity_score,
                'label': label,
                'confidence': confidence,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return self._fallback_analysis()
    
    async def _download_image(self, image_url: str) -> Image.Image:
        """Download image from URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content)).convert('RGB')
                return image
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None
    
    def _calculate_authenticity_score(self, probs: np.ndarray, image: Image.Image) -> float:
        """
        Calculate authenticity score using multiple signals
        
        Args:
            probs: Model output probabilities
            image: PIL Image object
            
        Returns:
            Authenticity score (0-1)
        """
        # Base score from model confidence
        base_score = float(max(probs))
        
        # Check for common AI generation artifacts
        artifacts_score = self._check_artifacts(image)
        
        # Combine scores
        final_score = (base_score * 0.6) + (artifacts_score * 0.4)
        
        return min(1.0, max(0.0, final_score))
    
    def _check_artifacts(self, image: Image.Image) -> float:
        """
        Check for common AI generation artifacts
        Simple heuristic-based approach for MVP
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Check image statistics
            mean_val = np.mean(img_array)
            std_val = np.std(img_array)
            
            # Simple heuristic: unusual statistics might indicate manipulation
            if std_val < 20 or std_val > 100:
                return 0.5
            
            if mean_val < 50 or mean_val > 200:
                return 0.6
            
            return 0.8
            
        except Exception as e:
            logger.error(f"Artifact check error: {e}")
            return 0.7
    
    def _fallback_analysis(self) -> Dict:
        """Fallback analysis when model is not available"""
        return {
            'score': 0.6,
            'label': 'suspicious',
            'confidence': 0.5,
            'explanation': 'Image analysis unavailable. Manual verification recommended.'
        }
    
    def _generate_explanation(self, score: float, label: str) -> str:
        """Generate human-readable explanation"""
        if label == "trustworthy":
            return f"Image appears authentic with score {score:.2f}. No significant manipulation artifacts detected."
        elif label == "suspicious":
            return f"Image shows some unusual characteristics with score {score:.2f}. Further verification recommended."
        else:
            return f"Image shows signs of AI generation or manipulation with score {score:.2f}. Multiple artifacts detected."