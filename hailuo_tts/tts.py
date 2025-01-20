import os
import requests
from typing import Optional, Dict, Any, Union, Tuple
from urllib3 import Retry
from requests.adapters import HTTPAdapter

class TTSMixin:
    """
    Mixin for Text-to-Speech functionality
    """
    
    def _download_audio(self, url: str, output_path: str) -> Optional[str]:
        """
        Download audio from URL and save to file
        
        Args:
            url: URL to download from
            output_path: Path to save the file (without extension)
            
        Returns:
            Optional[str]: Path to saved file or None if download failed
        """
        try:
            print(f"Downloading audio from {url}")
            
            # Setup session with timeout and retries
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=0.5)
            session.mount('https://', HTTPAdapter(max_retries=retries))
            
            response = session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Add .mp3 extension if missing
            if not output_path.endswith('.mp3'):
                output_path = f"{output_path}.mp3"

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

            # Save file in chunks to save memory
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Audio successfully saved to {output_path}")
            return output_path
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading audio: {str(e)}")
            return None
        except IOError as e:
            print(f"Error saving file: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None

    def set_voice(self, voice_id: str) -> None:
        """
        Set voice ID for TTS
        
        Args:
            voice_id: One of the supported voice IDs or a cloned voice ID
        """
        if not isinstance(voice_id, str):
            raise ValueError("Voice ID must be a string")
        self.voice_settings["voice_id"] = voice_id

    def set_voice_params(self, speed: Optional[float] = None, 
                        volume: Optional[float] = None, 
                        pitch: Optional[int] = None) -> None:
        """
        Set voice parameters
        
        Args:
            speed: Speech speed (0.5 to 2.0)
            volume: Speech volume (0 to 10)
            pitch: Speech pitch (-12 to 12)
        """
        if speed is not None:
            if not self.VOICE_CONSTRAINTS["speed"]["min"] <= speed <= self.VOICE_CONSTRAINTS["speed"]["max"]:
                raise ValueError(
                    f"Speed must be between {self.VOICE_CONSTRAINTS['speed']['min']} "
                    f"and {self.VOICE_CONSTRAINTS['speed']['max']}"
                )
            self.voice_settings["speed"] = speed
            
        if volume is not None:
            if not self.VOICE_CONSTRAINTS["volume"]["min"] < volume <= self.VOICE_CONSTRAINTS["volume"]["max"]:
                raise ValueError(
                    f"Volume must be between {self.VOICE_CONSTRAINTS['volume']['min']} "
                    f"and {self.VOICE_CONSTRAINTS['volume']['max']}"
                )
            self.voice_settings["vol"] = volume
            
        if pitch is not None:
            if not self.VOICE_CONSTRAINTS["pitch"]["min"] <= pitch <= self.VOICE_CONSTRAINTS["pitch"]["max"]:
                raise ValueError(
                    f"Pitch must be between {self.VOICE_CONSTRAINTS['pitch']['min']} "
                    f"and {self.VOICE_CONSTRAINTS['pitch']['max']}"
                )
            self.voice_settings["pitch"] = pitch

    def set_emotion(self, emotion: Optional[str] = None) -> None:
        """
        Set emotion for speech-01-turbo model
        
        Args:
            emotion: One of the supported emotions or None to disable
        """
        if emotion is not None:
            if self.model != "speech-01-turbo":
                raise ValueError("Emotions are only supported in speech-01-turbo model")
            if emotion not in self.EMOTIONS:
                raise ValueError(f"Invalid emotion. Choose from: {self.EMOTIONS}")
        self.emotion = emotion

    def set_language_boost(self, language: Optional[str] = None) -> None:
        """
        Set language boost for better language recognition
        
        Args:
            language: One of the supported languages or None to disable
        """
        if language is not None and language not in self.SUPPORTED_LANGUAGES:
            self.language_boost = "auto"
        else:
            self.language_boost = language

    def text_to_speech(self, text: str, output_path: str = "output", 
                      format: Optional[str] = "mp3", stream: bool = False) -> None:
        """
        Convert text to speech and save to file
        
        Args:
            text: Text to convert (max 5000 chars)
            output_path: Path to save the audio file (without extension)
            format: Audio format - "mp3", "pcm", or "flac"
            stream: Whether to stream the audio
            
        Note:
            To add pauses in text, use <#x#> where x is seconds (0.01-99.99)
            Example: "Hello<#1.5#>World" - adds 1.5 second pause between words
        """
        if len(text) > 5000:
            raise ValueError("Text length exceeds 5000 characters limit")

        if format:
            if format not in self.AUDIO_CONSTRAINTS["format"]:
                raise ValueError(f"Invalid format. Choose from: {self.AUDIO_CONSTRAINTS['format']}")
            self.audio_settings["format"] = format

        current_format = self.audio_settings["format"]
        
        # Ensure output path has correct extension
        if not output_path.endswith(f".{current_format}"):
            output_path = f"{output_path}.{current_format}"

        payload = {
            "model": self.model,
            "text": text,
            "stream": stream,
            "voice_setting": self.voice_settings,
            "audio_setting": self.audio_settings
        }

        if self.emotion and self.model == "speech-01-turbo":
            payload["voice_setting"]["emotion"] = self.emotion
            
        if self.language_boost:
            payload["language_boost"] = self.language_boost

        response = requests.post(
            f"{self.API_URL}?GroupId={self.group_id}",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.text}")
            
        response_data = response.json()
        
        # Save audio to file
        if response_data.get("data") and response_data["data"].get("audio"):
            audio_hex = response_data["data"]["audio"]
            audio_bytes = bytes.fromhex(audio_hex)
            
            # Create directory only if path contains directories
            if os.path.dirname(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
                
            # Print extra info if available
            if "extra_info" in response_data:
                print("\nAudio Information:")
                for key, value in response_data["extra_info"].items():
                    print(f"{key}: {value}")
        else:
            raise Exception("No audio data in response")