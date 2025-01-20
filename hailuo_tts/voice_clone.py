import os
import requests
from typing import Dict, Any, Optional, Tuple

class VoiceCloneMixin:
    """
    Mixin for voice cloning functionality
    """
    
    def upload_voice_file(self, file_path: str) -> str:
        """
        Upload audio file for voice cloning
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            str: file_id
            
        Requirements:
            - Format: MP3, M4A, WAV
            - Duration: 10 seconds to 5 minutes
            - Size: less than 20MB
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format or size is invalid
            Exception: If upload fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Check file extension
        file_ext = os.path.splitext(file_path)[1][1:].lower()
        if file_ext not in self.CLONE_FORMATS:
            raise ValueError(f"Unsupported file format. Must be one of: {self.CLONE_FORMATS}")
            
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_CLONE_FILE_SIZE:
            raise ValueError(f"File size exceeds 20MB limit: {file_size / (1024*1024):.2f}MB")
            
        url = f'https://api.minimaxi.chat/v1/files/upload?GroupId={self.group_id}'
        headers = {
            'authority': 'api.minimaxi.chat',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {'purpose': 'voice_clone'}
        files = {'file': open(file_path, 'rb')}
        
        response = requests.post(url, headers=headers, data=data, files=files)
        
        if response.status_code != 200:
            raise Exception(f"File upload failed: {response.text}")
            
        response_data = response.json()
        if 'file' not in response_data or 'file_id' not in response_data['file']:
            raise Exception("Invalid response from file upload API")
            
        return response_data['file']['file_id']

    def clone_voice(self, file_id: str, voice_id: str, output_path: str = "demo", 
                   noise_reduction: bool = False, preview_text: Optional[str] = "Test voice", 
                   preview_model: str = "speech-01-turbo", accuracy: float = 0.7, 
                   volume_normalize: bool = False) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Clone voice from uploaded audio file and download demo if available
        
        Args:
            file_id: ID of the uploaded audio file
            voice_id: Custom voice ID (min 8 chars, must contain letters and numbers, start with letter)
            output_path: Path to save the demo audio (without extension)
            noise_reduction: Enable noise reduction
            preview_text: Optional text for preview (max 300 chars)
            preview_model: Model for preview
            accuracy: Accuracy threshold (0-1)
            volume_normalize: Enable volume normalization
            
        Returns:
            Tuple[Dict[str, Any], Optional[str]]: (API response, demo audio path if available)
            
        Note:
            Cloned voice is temporary and will be deleted after 168 hours (7 days)
            unless used in T2A v2 API during this period.
            
        Raises:
            ValueError: If voice_id format is invalid or preview text is too long
            Exception: If cloning fails
        """
        # Validate voice_id
        if not voice_id or len(voice_id) < 8 or not voice_id[0].isalpha() or not any(c.isdigit() for c in voice_id):
            raise ValueError("Invalid voice_id. Must be at least 8 chars, contain letters and numbers, start with letter")
            
        if preview_text and len(preview_text) > 300:
            raise ValueError("Preview text exceeds 300 characters limit")
            
        if not 0 <= accuracy <= 1:
            raise ValueError("Accuracy must be between 0 and 1")
            
        payload = {
            "file_id": file_id,
            "voice_id": voice_id,
            "noise_reduction": noise_reduction,
            "need_volume_normalize": volume_normalize
        }
        
        if preview_text:
            payload.update({
                "text": preview_text,
                "model": preview_model
            })
            
        if accuracy != 0.7:  # Only include if different from default
            payload["accuracy"] = accuracy
            
        url = f"https://api.minimaxi.chat/v1/voice_clone?GroupId={self.group_id}"
        headers = {
            'authorization': f'Bearer {self.api_key}',
            'content-type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Voice cloning failed: {response.text}")
            
        response_data = response.json()
        demo_path = None
        
        # Download demo audio if available
        if 'demo_audio' in response_data:
            demo_url = response_data['demo_audio']
            demo_path = self._download_audio(demo_url, output_path)
            
        return response_data, demo_path