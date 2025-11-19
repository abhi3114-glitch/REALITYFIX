"""
Model Loader - Loads and manages pretrained ML models
Handles model initialization and caching
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelLoader:
    """Manages loading and caching of ML models"""
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
    
    def load_text_model(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Load pretrained text classification model
        
        Args:
            model_name: HuggingFace model identifier
            
        Returns:
            Tuple of (model, tokenizer)
        """
        try:
            if model_name in self.models:
                logger.info(f"Using cached model: {model_name}")
                return self.models[model_name], self.tokenizers[model_name]
            
            logger.info(f"Loading text model: {model_name}")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            model.to(self.device)
            model.eval()
            
            # Cache for future use
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            
            logger.info(f"Successfully loaded: {model_name}")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load text model: {e}")
            raise
    
    def load_image_model(self):
        """
        Load pretrained image forensics model
        For MVP, we'll use a simple ResNet-based approach
        
        Returns:
            Image classification model
        """
        try:
            model_name = "resnet18"
            
            if model_name in self.models:
                logger.info(f"Using cached model: {model_name}")
                return self.models[model_name]
            
            logger.info(f"Loading image model: {model_name}")
            
            # Load pretrained ResNet
            from torchvision import models
            model = models.resnet18(pretrained=True)
            model.to(self.device)
            model.eval()
            
            # Cache for future use
            self.models[model_name] = model
            
            logger.info(f"Successfully loaded: {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load image model: {e}")
            raise
    
    def load_audio_model(self):
        """
        Load pretrained audio deepfake detection model
        For MVP, we'll use a simple CNN-based approach
        
        Returns:
            Audio classification model
        """
        try:
            model_name = "audio_cnn"
            
            if model_name in self.models:
                logger.info(f"Using cached model: {model_name}")
                return self.models[model_name]
            
            logger.info(f"Loading audio model: {model_name}")
            
            # For MVP, create a simple CNN model
            # In production, use pretrained ASVspoof or similar
            model = self._create_simple_audio_model()
            model.to(self.device)
            model.eval()
            
            # Cache for future use
            self.models[model_name] = model
            
            logger.info(f"Successfully loaded: {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load audio model: {e}")
            raise
    
    def _create_simple_audio_model(self):
        """Create a simple CNN for audio classification"""
        import torch.nn as nn
        
        class SimpleCNN(nn.Module):
            def __init__(self):
                super(SimpleCNN, self).__init__()
                self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
                self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
                self.pool = nn.MaxPool2d(2, 2)
                self.fc1 = nn.Linear(64 * 32 * 32, 128)
                self.fc2 = nn.Linear(128, 2)
                self.relu = nn.ReLU()
                self.dropout = nn.Dropout(0.5)
            
            def forward(self, x):
                x = self.pool(self.relu(self.conv1(x)))
                x = self.pool(self.relu(self.conv2(x)))
                x = x.view(-1, 64 * 32 * 32)
                x = self.dropout(self.relu(self.fc1(x)))
                x = self.fc2(x)
                return x
        
        return SimpleCNN()
    
    def get_device(self):
        """Get current device (CPU or CUDA)"""
        return self.device

# Global model loader instance
model_loader = ModelLoader()