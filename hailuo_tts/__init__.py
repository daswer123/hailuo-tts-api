from typing import Optional, Dict, Any, Union, Tuple
import requests
import os
from urllib3 import Retry
from requests.adapters import HTTPAdapter

from .tts import TTSMixin
from .voice_clone import VoiceCloneMixin

class HailuoTTS(TTSMixin, VoiceCloneMixin):
    """
    Main wrapper class for Hailuo TTS API text-to-speech functionality
    """
    
    # API Constants
    API_URL = "https://api.minimaxi.chat/v1/t2a_v2"
    
    # Available models
    MODELS = {
        "turbo": "speech-01-turbo",  # Latest model, excellent performance and low latency
        "hd": "speech-01-hd"         # Rich voices, expressive emotions, authentic languages
    }
    
    # Supported emotions (only for speech-01-turbo)
    EMOTIONS = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"]
    
    # Supported voices
    VOICES = [
        "Wise_Woman", "Friendly_Person", "Inspirational_girl", "Deep_Voice_Man",
        "Calm_Woman", "Casual_Guy", "Lively_Girl", "Patient_Man", "Young_Knight",
        "Determined_Man", "Lovely_Girl", "Decent_Boy", "Imposing_Manner",
        "Elegant_Man", "Abbess", "Sweet_Girl_2", "Exuberant_Girl"
    ]
    
    # Supported languages for language boost
    SUPPORTED_LANGUAGES = [
        'Spanish', 'French', 'Portuguese', 'Korean', 'Indonesian', 'German',
        'Japanese', 'Italian', 'Chinese', 'Chinese,Yue', 'auto'
    ]

    # Audio settings constraints
    AUDIO_CONSTRAINTS = {
        "sample_rate": [8000, 16000, 22050, 24000, 32000],  # Default: 32000
        "bitrate": [32000, 64000, 128000],                  # Default: 128000
        "format": ["mp3", "pcm", "flac"],                   # Default: mp3
        "channel": [1, 2]                                   # Default: 1 (mono)
    }
    
    # Voice settings constraints
    VOICE_CONSTRAINTS = {
        "speed": {"min": 0.5, "max": 2.0, "default": 1.0},    # Speech speed
        "volume": {"min": 0, "max": 10, "default": 1.0},      # Speech volume
        "pitch": {"min": -12, "max": 12, "default": 0}        # Speech pitch
    }
    
    # Voice clone supported formats
    CLONE_FORMATS = ["mp3", "m4a", "wav"]
    
    # Maximum file size for voice cloning (20MB in bytes)
    MAX_CLONE_FILE_SIZE = 20 * 1024 * 1024

    @classmethod
    def create(cls, 
               api_key: str,
               group_id: str,
               model: str = "hd") -> 'HailuoTTS':
        """
        Creates and initializes a new HailuoTTS instance with minimal required parameters.
        
        Args:
            api_key: API key for authentication
            group_id: Group ID for API access
            model: TTS model ('turbo' or 'hd', default: 'hd')
            
        Returns:
            HailuoTTS: New instance with default settings
            
        Raises:
            ValueError: If API key validation fails or model is invalid
        """
        instance = cls()
        
        # Validate and set API parameters
        if not api_key or not api_key[0].isalpha():
            raise ValueError("Invalid API key format")
            
        instance.api_key = api_key
        instance.group_id = group_id
        
        # Validate and set model
        if model not in instance.MODELS:
            raise ValueError(f"Invalid model. Choose from: {list(instance.MODELS.keys())}")
        instance.model = instance.MODELS[model]
        
        # Set default headers
        instance.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {instance.api_key}"
        }
        
        # Initialize with default settings
        instance._init_default_settings()
        
        return instance
    
    def _init_default_settings(self):
        """Initialize default voice and audio settings"""
        self.voice_settings = {
            "voice_id": "Friendly_Person",
            "speed": self.VOICE_CONSTRAINTS["speed"]["default"],
            "vol": self.VOICE_CONSTRAINTS["volume"]["default"],
            "pitch": self.VOICE_CONSTRAINTS["pitch"]["default"]
        }
        
        self.audio_settings = {
            "sample_rate": self.AUDIO_CONSTRAINTS["sample_rate"][-1],  # 32000
            "bitrate": self.AUDIO_CONSTRAINTS["bitrate"][-1],          # 128000
            "format": self.AUDIO_CONSTRAINTS["format"][0],             # mp3
            "channel": self.AUDIO_CONSTRAINTS["channel"][0]            # mono
        }
        
        self.language_boost = None
        self.emotion = None

    def get_available_models(self) -> Dict[str, str]:
        """Get available TTS models with descriptions"""
        return {
            "turbo": "Latest model, excellent performance and low latency",
            "hd": "Rich voices, expressive emotions, authentic languages"
        }

    def get_available_voices(self) -> list:
        """Get list of available system voices"""
        return self.VOICES.copy()

    def get_available_emotions(self) -> list:
        """Get list of available emotions (only for turbo model)"""
        return self.EMOTIONS.copy()

    def get_available_languages(self) -> list:
        """Get list of supported languages for language boost"""
        return self.SUPPORTED_LANGUAGES.copy()

    def get_audio_constraints(self) -> Dict[str, list]:
        """Get audio settings constraints"""
        return self.AUDIO_CONSTRAINTS.copy()

    def get_voice_constraints(self) -> Dict[str, Dict[str, float]]:
        """Get voice settings constraints"""
        return self.VOICE_CONSTRAINTS.copy()

    def set_model(self, model: str) -> None:
        """Set TTS model"""
        if model not in self.MODELS:
            raise ValueError(f"Invalid model. Choose from: {list(self.MODELS.keys())}")
        self.model = self.MODELS[model]

    def update_api_settings(self, api_key: Optional[str] = None, 
                          group_id: Optional[str] = None) -> None:
        """
        Update API settings
        
        Args:
            api_key: New API key
            group_id: New group ID
        """
        if api_key:
            if not api_key[0].isalpha():
                raise ValueError("Invalid API key format")
            self.api_key = api_key
            self.headers["Authorization"] = f"Bearer {api_key}"
            
        if group_id:
            self.group_id = group_id

    def update_audio_settings(self, sample_rate: Optional[int] = None,
                            bitrate: Optional[int] = None,
                            format: Optional[str] = None,
                            channel: Optional[int] = None) -> None:
        """
        Update audio settings
        
        Args:
            sample_rate: Sample rate (8000, 16000, 22050, 24000, 32000)
            bitrate: Bitrate (32000, 64000, 128000)
            format: Audio format (mp3, pcm, flac)
            channel: Number of channels (1: mono, 2: stereo)
        """
        if sample_rate and sample_rate not in self.AUDIO_CONSTRAINTS["sample_rate"]:
            raise ValueError(f"Invalid sample rate. Choose from: {self.AUDIO_CONSTRAINTS['sample_rate']}")
            
        if bitrate and bitrate not in self.AUDIO_CONSTRAINTS["bitrate"]:
            raise ValueError(f"Invalid bitrate. Choose from: {self.AUDIO_CONSTRAINTS['bitrate']}")
            
        if format and format not in self.AUDIO_CONSTRAINTS["format"]:
            raise ValueError(f"Invalid format. Choose from: {self.AUDIO_CONSTRAINTS['format']}")
            
        if channel and channel not in self.AUDIO_CONSTRAINTS["channel"]:
            raise ValueError(f"Invalid channel. Choose from: {self.AUDIO_CONSTRAINTS['channel']}")
            
        if sample_rate:
            self.audio_settings["sample_rate"] = sample_rate
        if bitrate:
            self.audio_settings["bitrate"] = bitrate
        if format:
            self.audio_settings["format"] = format
        if channel:
            self.audio_settings["channel"] = channel

    def update_model(self, model: str) -> None:
        """
        Update TTS model
        
        Args:
            model: New model ('turbo' or 'hd')
        """
        if model not in self.MODELS:
            raise ValueError(f"Invalid model. Choose from: {list(self.MODELS.keys())}")
        self.model = self.MODELS[model]
        
        # Reset emotion if switching from turbo to hd
        if model == "hd" and self.emotion:
            self.emotion = None