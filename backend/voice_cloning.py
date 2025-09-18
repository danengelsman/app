import os
import aiohttp
import aiofiles
import asyncio
import logging
import time
import json
import hashlib
import soundfile as sf
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException, UploadFile, File, Form
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceCloneStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class VoiceCloneJob:
    job_id: str
    voice_id: str
    file_id: Optional[str] = None
    status: VoiceCloneStatus = VoiceCloneStatus.PENDING
    preview_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

# Pydantic models for request/response validation
class VoiceCloneRequest(BaseModel):
    voice_id: str = Field(..., min_length=3, max_length=50)
    preview_text: Optional[str] = Field(None, max_length=300)
    model: str = Field("speech-01", description="Model to use for voice cloning")
    
    @validator('voice_id')
    def validate_voice_id(cls, v):
        # Allow alphanumeric characters, underscores, and hyphens
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('voice_id must contain only letters, numbers, underscores, and hyphens')
        return v

class VoiceCloneResponse(BaseModel):
    voice_id: str
    file_id: str
    status: str
    message: str
    preview_audio_url: Optional[str] = None
    job_id: str

class TTSRequest(BaseModel):
    text: str = Field(..., max_length=1000)
    voice_id: str
    model: str = Field("speech-01", description="Model to use for TTS")

class TTSResponse(BaseModel):
    audio_url: str
    status: str
    duration: Optional[float] = None

class MinimaxAuth:
    """Handle Minimax API authentication"""
    
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")
        
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY environment variable not set")
        if not self.group_id:
            raise ValueError("MINIMAX_GROUP_ID environment variable not set")
    
    def get_headers(self) -> Dict[str, str]:
        """Generate authentication headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_upload_headers(self) -> Dict[str, str]:
        """Generate headers for file upload requests"""
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

class AudioFileHandler:
    """Handle audio file validation and processing"""
    
    SUPPORTED_FORMATS = {'.mp3', '.m4a', '.wav'}
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    MIN_DURATION = 10  # seconds
    MAX_DURATION = 300  # 5 minutes
    
    def __init__(self, upload_dir: str = "temp_uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def validate_audio_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded audio file format, size, and duration"""
        try:
            # Check file extension
            if not file.filename:
                return False, "No filename provided"
                
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                return False, f"Unsupported format. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            
            # Check file size
            content = await file.read()
            if len(content) > self.MAX_FILE_SIZE:
                return False, f"File too large. Maximum size: {self.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            
            # Reset file pointer
            await file.seek(0)
            
            # Save temporary file for duration check
            temp_path = await self.save_temp_file(file, content)
            
            try:
                # Check audio duration using soundfile
                with sf.SoundFile(temp_path) as audio_file:
                    duration = len(audio_file) / audio_file.samplerate
                    
                if duration < self.MIN_DURATION:
                    return False, f"Audio too short. Minimum: {self.MIN_DURATION}s"
                if duration > self.MAX_DURATION:
                    return False, f"Audio too long. Maximum: {self.MAX_DURATION}s"
                
                return True, f"Valid audio file ({duration:.1f}s)"
                
            finally:
                # Clean up temporary file
                if temp_path.exists():
                    await aiofiles.os.remove(temp_path)
                
        except Exception as e:
            logger.error(f"Audio validation error: {str(e)}")
            return False, f"Invalid audio file: {str(e)}"
    
    async def save_temp_file(self, file: UploadFile, content: bytes = None) -> Path:
        """Save uploaded file to temporary location"""
        if content is None:
            content = await file.read()
        
        # Generate unique filename
        file_hash = hashlib.md5(content).hexdigest()[:8]
        file_ext = Path(file.filename).suffix.lower()
        temp_filename = f"{file_hash}_{int(datetime.now().timestamp())}{file_ext}"
        temp_path = self.upload_dir / temp_filename
        
        async with aiofiles.open(temp_path, 'wb') as temp_file:
            await temp_file.write(content)
        
        return temp_path
    
    async def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove temporary files older than specified age"""
        current_time = datetime.now().timestamp()
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (max_age_hours * 3600):
                    await aiofiles.os.remove(file_path)
                    logger.info(f"Cleaned up old file: {file_path}")

class MinimaxClient:
    """Minimax API client for voice cloning operations"""
    
    def __init__(self, auth: MinimaxAuth):
        self.auth = auth
        self.base_url = "https://api.minimaxi.chat/v1"
        self.session = None
        self.jobs: Dict[str, VoiceCloneJob] = {}
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=300, connect=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def upload_audio_file(self, file_path: Path, purpose: str = "voice_clone") -> str:
        """Upload audio file and return file_id"""
        url = f"{self.base_url}/files"
        params = {"GroupId": self.auth.group_id}
        headers = self.auth.get_upload_headers()
        
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                file_content = await file.read()
            
            data = aiohttp.FormData()
            data.add_field('purpose', purpose)
            data.add_field(
                'file', 
                file_content,
                filename=file_path.name,
                content_type=self._get_content_type(file_path.suffix)
            )
            
            async with self.session.post(url, params=params, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    file_id = result.get("file_id")
                    if not file_id:
                        raise ValueError("No file_id in response")
                    
                    logger.info(f"File uploaded successfully: {file_id}")
                    return file_id
                else:
                    error_text = await response.text()
                    logger.error(f"File upload failed: {response.status} - {error_text}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"File upload failed: {error_text}"
                    )
                    
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")
    
    async def create_voice_clone(
        self, 
        file_id: str, 
        voice_id: str,
        **kwargs
    ) -> VoiceCloneJob:
        """Create voice clone from uploaded file"""
        url = f"{self.base_url}/voice_clone"
        params = {"GroupId": self.auth.group_id}
        headers = self.auth.get_headers()
        
        payload = {
            "file_id": file_id,
            "voice_id": voice_id,
            "model": kwargs.get("model", "speech-01")
        }
        
        # Add preview text if provided
        if "text" in kwargs and kwargs["text"]:
            payload["text"] = kwargs["text"]
        
        try:
            async with self.session.post(url, params=params, headers=headers, json=payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = await response.json()
                    
                    job = VoiceCloneJob(
                        job_id=f"clone_{voice_id}_{int(datetime.now().timestamp())}",
                        voice_id=voice_id,
                        file_id=file_id,
                        status=VoiceCloneStatus.COMPLETED,
                        created_at=datetime.now()
                    )
                    
                    # Extract preview URL if available
                    if "preview_url" in result:
                        job.preview_url = result["preview_url"]
                    elif "audio_url" in result:
                        job.preview_url = result["audio_url"]
                    
                    self.jobs[job.job_id] = job
                    logger.info(f"Voice clone created: {voice_id}")
                    return job
                else:
                    logger.error(f"Voice clone failed: {response.status} - {response_text}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Voice clone failed: {response_text}"
                    )
                    
        except Exception as e:
            logger.error(f"Voice clone error: {str(e)}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Voice clone error: {str(e)}")
    
    async def generate_speech(
        self, 
        text: str, 
        voice_id: str, 
        model: str = "speech-01"
    ) -> str:
        """Generate speech using cloned voice"""
        url = f"{self.base_url}/t2a_pro"
        params = {"GroupId": self.auth.group_id}
        headers = self.auth.get_headers()
        
        payload = {
            "model": model,
            "voice_id": voice_id,
            "text": text,
            "stream": False
        }
        
        try:
            async with self.session.post(url, params=params, headers=headers, json=payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = await response.json()
                    audio_url = result.get("audio_url")
                    if not audio_url:
                        raise ValueError("No audio_url in response")
                    
                    logger.info(f"Speech generated for voice: {voice_id}")
                    return audio_url
                else:
                    logger.error(f"Speech generation failed: {response.status} - {response_text}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Speech generation failed: {response_text}"
                    )
                    
        except Exception as e:
            logger.error(f"Speech generation error: {str(e)}")
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Speech generation error: {str(e)}")
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        content_types = {
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4', 
            '.wav': 'audio/wav'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')

class VoiceCloneManager:
    """High-level manager for voice cloning operations"""
    
    def __init__(self):
        self.auth = MinimaxAuth()
        self.audio_handler = AudioFileHandler()
        self.client = None
    
    async def validate_credentials(self) -> bool:
        """Test API credentials"""
        try:
            async with MinimaxClient(self.auth) as client:
                # Try to make a simple API call to test credentials
                url = f"{client.base_url}/files"
                params = {"GroupId": self.auth.group_id}
                headers = self.auth.get_headers()
                
                async with client.session.get(url, params=params, headers=headers) as response:
                    return response.status in [200, 404]  # 404 might mean no files, but auth is OK
        except Exception as e:
            logger.error(f"Credential validation failed: {str(e)}")
            return False
    
    async def create_voice_clone_from_upload(
        self,
        file: UploadFile,
        voice_id: str,
        preview_text: Optional[str] = None,
        model: str = "speech-01"
    ) -> VoiceCloneJob:
        """Complete workflow to create voice clone from uploaded file"""
        
        # Validate audio file
        is_valid, validation_message = await self.audio_handler.validate_audio_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_message)
        
        # Save temporary file
        temp_path = await self.audio_handler.save_temp_file(file)
        
        try:
            async with MinimaxClient(self.auth) as client:
                # Upload file to MiniMax
                file_id = await client.upload_audio_file(temp_path)
                
                # Create voice clone
                job = await client.create_voice_clone(
                    file_id=file_id,
                    voice_id=voice_id,
                    text=preview_text,
                    model=model
                )
                
                return job
                
        finally:
            # Clean up temporary file
            if temp_path.exists():
                await aiofiles.os.remove(temp_path)
    
    async def generate_speech_with_voice(
        self,
        text: str,
        voice_id: str,
        model: str = "speech-01"
    ) -> str:
        """Generate speech using a cloned voice"""
        async with MinimaxClient(self.auth) as client:
            return await client.generate_speech(text, voice_id, model)
    
    async def cleanup_old_files(self):
        """Clean up old temporary files"""
        await self.audio_handler.cleanup_old_files()

# Global instance
voice_clone_manager = VoiceCloneManager()