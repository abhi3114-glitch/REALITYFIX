"""
Audio Detector - Analyzes audio for deepfake detection
Uses spectral analysis and pretrained models
"""

import torch
import numpy as np
from typing import Dict
import logging
import httpx
import librosa
from io import BytesIO
from model_loader import model_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioDetector:
    """Detects deepfake audio"""
    
    def __init__(self):
        self.model = None
        self.sample_rate = 16000
        self._load_model()
    
    def _load_model(self):
        """Load pretrained audio classification model"""
        try:
            self.model = model_loader.load_audio_model()
            logger.info("Audio detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio detector: {e}")
            self.model = None
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    async def analyze(self, audio_url: str) -> Dict:
        """
        Analyze audio for deepfake detection
        
        Args:
            audio_url: URL of the audio file to analyze
            
        Returns:
            Dictionary with score, label, confidence, and explanation
        """
        try:
            # Download and load audio
            audio_data = await self._download_audio(audio_url)
            
            if audio_data is None:
                return self._fallback_analysis()
            
            if not self.is_loaded():
                logger.warning("Model not loaded, using fallback analysis")
                return self._fallback_analysis()
            
            # Extract features
            features = self._extract_features(audio_data)
            
            # Get predictions
            authenticity_score = self._predict(features)
            
            # Determine label
            if authenticity_score >= 0.7:
                label = "trustworthy"
            elif authenticity_score >= 0.4:
                label = "suspicious"
            else:
                label = "misinformation"
            
            # Calculate confidence
            confidence = min(0.85, 0.6 + abs(authenticity_score - 0.5))
            
            # Generate explanation
            explanation = self._generate_explanation(authenticity_score, label)
            
            return {
                'score': authenticity_score,
                'label': label,
                'confidence': confidence,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            return self._fallback_analysis()
    
    async def _download_audio(self, audio_url: str) -> np.ndarray:
        """Download and load audio from URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                
                # Load audio using librosa
                audio_data, sr = librosa.load(
                    BytesIO(response.content),
                    sr=self.sample_rate,
                    duration=30.0  # Limit to 30 seconds
                )
                return audio_data
                
        except Exception as e:
            logger.error(f"Failed to download audio: {e}")
            return None
    
    def _extract_features(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Extract audio features for analysis
        
        Args:
            audio_data: Audio waveform as numpy array
            
        Returns:
            Feature tensor for model input
        """
        try:
            # Extract mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data,
                sr=self.sample_rate,
                n_mels=128,
                fmax=8000
            )
            
            # Convert to log scale
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Normalize
            log_mel_spec = (log_mel_spec - log_mel_spec.mean()) / (log_mel_spec.std() + 1e-6)
            
            # Resize to fixed size (128x128)
            if log_mel_spec.shape[1] > 128:
                log_mel_spec = log_mel_spec[:, :128]
            else:
                pad_width = 128 - log_mel_spec.shape[1]
                log_mel_spec = np.pad(log_mel_spec, ((0, 0), (0, pad_width)), mode='constant')
            
            # Convert to tensor
            features = torch.FloatTensor(log_mel_spec).unsqueeze(0).unsqueeze(0)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            raise
    
    def _predict(self, features: torch.Tensor) -> float:
        """
        Predict authenticity score
        
        Args:
            features: Feature tensor
            
        Returns:
            Authenticity score (0-1)
        """
        try:
            # Move to device
            device = model_loader.get_device()
            features = features.to(device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(features)
                probabilities = torch.softmax(outputs, dim=-1)
            
            # Extract authenticity score (assuming class 1 is authentic)
            score = float(probabilities[0][1].cpu().numpy())
            
            return score
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.6  # Default to suspicious
    
    def _fallback_analysis(self) -> Dict:
        """Fallback analysis when model is not available"""
        return {
            'score': 0.6,
            'label': 'suspicious',
            'confidence': 0.5,
            'explanation': 'Audio analysis unavailable. Manual verification recommended.'
        }
    
    def _generate_explanation(self, score: float, label: str) -> str:
        """Generate human-readable explanation"""
        if label == "trustworthy":
            return f"Audio appears authentic with score {score:.2f}. Spectral analysis shows natural voice characteristics."
        elif label == "suspicious":
            return f"Audio shows some unusual patterns with score {score:.2f}. Further verification recommended."
        else:
            return f"Audio shows signs of synthesis or manipulation with score {score:.2f}. Spectral artifacts detected."