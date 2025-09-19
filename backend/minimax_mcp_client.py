import os
import asyncio
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import aiofiles
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field
from fastapi import HTTPException, UploadFile

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
    file_path: Optional[str] = None
    status: VoiceCloneStatus = VoiceCloneStatus.PENDING
    preview_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

# Pydantic models for request/response validation
class VoiceCloneRequest(BaseModel):
    voice_id: str = Field(..., min_length=8, max_length=256)
    preview_text: Optional[str] = Field(None, max_length=2000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": "my_custom_voice_01",
                "preview_text": "Hello, this is a preview of my cloned voice."
            }
        }

class VoiceCloneResponse(BaseModel):
    voice_id: str
    file_id: str
    job_id: str
    status: str
    message: str
    preview_audio_url: Optional[str] = None

class TTSRequest(BaseModel):
    text: str = Field(..., max_length=10000)
    voice_id: str
    model: str = Field("speech-02-hd", description="Model to use for TTS")
    speed: float = Field(1.0, ge=0.5, le=2.0)
    emotion: str = Field("happy", description="Emotional tone")

class TTSResponse(BaseModel):
    audio_path: str
    status: str
    duration: Optional[float] = None

class MinimaxMCPClient:
    """Client for interacting with MiniMax MCP server"""
    
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.api_host = os.getenv("MINIMAX_API_HOST", "https://api.minimax.io")
        self.base_path = os.getenv("MINIMAX_MCP_BASE_PATH", "/app/backend/temp_uploads")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")
        
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY environment variable not set")
        if not self.group_id:
            raise ValueError("MINIMAX_GROUP_ID environment variable not set")
        
        # Ensure base path exists
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        
        self.jobs: Dict[str, VoiceCloneJob] = {}
    
    async def validate_credentials(self) -> bool:
        """Test if MCP server can be accessed"""
        try:
            # Try to list voices to test credentials
            result = await self._run_mcp_tool("list_voices", {"voice_type": "system"})
            return result is not None
        except Exception as e:
            logger.error(f"Credential validation failed: {str(e)}")
            return False
    
    async def _run_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run a MiniMax MCP tool with the given parameters using actual MCP functions"""
        try:
            # Set environment variables for the MCP call
            old_env = {}
            for key, value in {
                "MINIMAX_API_KEY": self.api_key,
                "MINIMAX_API_HOST": self.api_host,
                "MINIMAX_MCP_BASE_PATH": self.base_path
            }.items():
                old_env[key] = os.environ.get(key)
                os.environ[key] = value
            
            try:
                # Force reload of MCP module to pick up environment variables
                import importlib
                import minimax_mcp.server
                importlib.reload(minimax_mcp.server)
                
                # Import MCP functions
                from minimax_mcp.server import voice_clone, text_to_audio, list_voices
                
                # Run MCP functions in thread pool since they're synchronous
                loop = asyncio.get_event_loop()
                
                if tool_name == "list_voices":
                    voice_type = parameters.get("voice_type", "all")
                    result = await loop.run_in_executor(None, list_voices, voice_type)
                    return result
                
                elif tool_name == "voice_clone":
                    voice_id = parameters.get("voice_id")
                    file_path = parameters.get("file")
                    text = parameters.get("text")
                    output_directory = parameters.get("output_directory", self.base_path)
                    is_url = parameters.get("is_url", False)
                    
                    logger.info(f"Calling MiniMax voice_clone: voice_id={voice_id}, file={file_path}")
                    
                    def run_voice_clone():
                        return voice_clone(
                            voice_id=voice_id,
                            file=file_path,
                            text=text,
                            output_directory=output_directory,
                            is_url=is_url
                        )
                    
                    result = await loop.run_in_executor(None, run_voice_clone)
                    return result
                
                elif tool_name == "text_to_audio":
                    text = parameters.get("text")
                    voice_id = parameters.get("voice_id")
                    model = parameters.get("model", "speech-02-hd")
                    speed = parameters.get("speed", 1.0)
                    emotion = parameters.get("emotion", "happy")
                    output_directory = parameters.get("output_directory", self.base_path)
                    format_type = parameters.get("format", "mp3")
                    
                    logger.info(f"Calling MiniMax text_to_audio: voice_id={voice_id}, text='{text[:50]}...'")
                    
                    def run_text_to_audio():
                        return text_to_audio(
                            text=text,
                            output_directory=output_directory,
                            voice_id=voice_id,
                            model=model,
                            speed=speed,
                            emotion=emotion,
                            format=format_type
                        )
                    
                    result = await loop.run_in_executor(None, run_text_to_audio)
                    return result
                
                else:
                    raise ValueError(f"Unknown MCP tool: {tool_name}")
                    
            finally:
                # Restore original environment variables
                for key, old_value in old_env.items():
                    if old_value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = old_value
                
        except Exception as e:
            logger.error(f"MCP tool execution error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"MCP tool error: {str(e)}")
    
    async def create_voice_clone(
        self,
        file_path: str,
        voice_id: str,
        preview_text: Optional[str] = None
    ) -> VoiceCloneJob:
        """Create a voice clone using MCP voice_clone tool"""
        
        job_id = f"clone_{voice_id}_{int(datetime.now().timestamp())}"
        
        try:
            # Prepare parameters for voice_clone tool
            parameters = {
                "voice_id": voice_id,
                "file": file_path,
                "output_directory": self.base_path,
                "is_url": False
            }
            
            if preview_text:
                parameters["text"] = preview_text
            
            # Call the MCP voice_clone tool
            logger.info(f"Calling MCP voice_clone tool with voice_id: {voice_id}")
            result = await self._run_mcp_tool("voice_clone", parameters)
            
            # Check for MCP errors
            if hasattr(result, 'text') and 'Failed to clone voice' in result.text:
                error_text = result.text
                if 'API Error' in error_text:
                    if '1000-unknown error' in error_text:
                        raise ValueError("Voice cloning failed: Invalid audio file format or API issue. Please ensure you upload a valid audio file (MP3, WAV, M4A) with actual audio content.")
                    elif 'rate limit' in error_text.lower():
                        raise ValueError("Voice cloning failed: API rate limit exceeded. Please try again in a few minutes.")
                    else:
                        raise ValueError(f"Voice cloning failed: {error_text}")
                else:
                    raise ValueError(f"Voice clone failed: {error_text}")
            
            # Create job record
            job = VoiceCloneJob(
                job_id=job_id,
                voice_id=voice_id,
                file_path=file_path,
                status=VoiceCloneStatus.COMPLETED,
                created_at=datetime.now()
            )
            
            # Check if a preview audio was created
            success_text = ""
            if hasattr(result, 'text'):
                success_text = result.text
            elif "content" in result and result["content"]:
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        success_text = content_item.get("text", "")
                        break
            
            # Look for created audio URLs in the success text
            if success_text:
                # Check for different URL patterns
                url_patterns = ["Demo audio URL:", "Audio URL:", "Preview URL:"]
                for pattern in url_patterns:
                    if pattern in success_text:
                        start = success_text.find(pattern) + len(pattern)
                        remaining = success_text[start:].strip()
                        potential_url = remaining.split()[0] if remaining.split() else None
                        if potential_url and potential_url.startswith("http"):
                            job.preview_url = potential_url
                            logger.info(f"Found preview audio URL: {potential_url[:50]}...")
                            break
            
            self.jobs[job_id] = job
            logger.info(f"Voice clone created successfully: {voice_id}")
            return job
            
        except Exception as e:
            logger.error(f"Voice clone creation failed: {str(e)}")
            
            # Create failed job record
            job = VoiceCloneJob(
                job_id=job_id,
                voice_id=voice_id,
                file_path=file_path,
                status=VoiceCloneStatus.FAILED,
                error_message=str(e),
                created_at=datetime.now()
            )
            self.jobs[job_id] = job
            raise HTTPException(status_code=500, detail=f"Voice clone failed: {str(e)}")
    
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        model: str = "speech-02-hd",
        speed: float = 1.0,
        emotion: str = "happy"
    ) -> str:
        """Generate speech using MCP text_to_audio tool"""
        
        try:
            # Prepare parameters for text_to_audio tool
            parameters = {
                "text": text,
                "voice_id": voice_id,
                "model": model,
                "speed": speed,
                "emotion": emotion,
                "output_directory": self.base_path,
                "format": "mp3"
            }
            
            logger.info(f"Calling MCP text_to_audio tool with voice_id: {voice_id}")
            result = await self._run_mcp_tool("text_to_audio", parameters)
            
            if "error" in result:
                raise ValueError(f"Speech generation failed: {result['error']}")
            
            # Extract audio URL from result
            audio_url = None
            
            # Handle direct TextContent response
            if hasattr(result, 'text'):
                text_content = result.text
                # Check for different URL patterns
                url_patterns = ["Audio URL:", "Demo audio URL:", "Preview URL:"]
                for pattern in url_patterns:
                    if pattern in text_content:
                        start = text_content.find(pattern) + len(pattern)
                        remaining = text_content[start:].strip()
                        audio_url = remaining.split()[0] if remaining.split() else None
                        if audio_url and audio_url.startswith("http"):
                            break
            
            # Handle legacy content format
            elif "content" in result and result["content"]:
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        text_content = content_item.get("text", "")
                        if "Audio URL:" in text_content:
                            start = text_content.find("Audio URL: ") + 11
                            remaining = text_content[start:]
                            audio_url = remaining.split()[0] if remaining.split() else None
                            break
            
            if not audio_url:
                # Log the actual response for debugging
                logger.error(f"No audio URL found in MCP response. Response: {result}")
                raise ValueError("No audio URL found in MCP response")
            
            logger.info(f"Speech generated successfully: {audio_url[:100]}...")
            return audio_url
            
        except Exception as e:
            logger.error(f"Speech generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")
    
    async def list_voices(self, voice_type: str = "all") -> List[Dict[str, Any]]:
        """List available voices using MCP list_voices tool"""
        
        try:
            parameters = {"voice_type": voice_type}
            
            logger.info(f"Calling MCP list_voices tool with type: {voice_type}")
            result = await self._run_mcp_tool("list_voices", parameters)
            
            if "error" in result:
                raise ValueError(f"List voices failed: {result['error']}")
            
            # Parse the result to extract voice information
            voices = []
            if "content" in result and result["content"]:
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        text_content = content_item.get("text", "")
                        # Parse voice information from text
                        # This is a simplified parser - adjust based on actual MCP response format
                        lines = text_content.split('\n')
                        for line in lines:
                            if 'voice_id' in line.lower() or 'id:' in line.lower():
                                voices.append({"text": line.strip()})
            
            return voices
            
        except Exception as e:
            logger.error(f"List voices failed: {str(e)}")
            return []

class VoiceCloneManager:
    """High-level manager for MCP-based voice cloning operations"""
    
    def __init__(self):
        self.client = MinimaxMCPClient()
    
    async def validate_credentials(self) -> bool:
        """Test MCP server credentials"""
        return await self.client.validate_credentials()
    
    async def save_uploaded_file(self, file: UploadFile) -> str:
        """Save uploaded file and return the path"""
        # Generate a unique filename
        file_ext = Path(file.filename).suffix.lower() if file.filename else '.mp3'
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = Path(self.client.base_path) / unique_filename
        
        # Save the file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            
            # Basic validation - check if content looks like audio
            if len(content) < 1000:  # Audio files should be at least 1KB
                raise HTTPException(
                    status_code=400, 
                    detail="File too small to be a valid audio file. Please upload a real audio file."
                )
            
            # Check for some common audio file headers
            if file_ext == '.mp3':
                if not (content.startswith(b'ID3') or content.startswith(b'\xff\xfb') or content.startswith(b'\xff\xf3')):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid MP3 file format. Please upload a valid MP3 audio file."
                    )
            elif file_ext == '.wav':
                if not content.startswith(b'RIFF'):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid WAV file format. Please upload a valid WAV audio file."
                    )
            
            await f.write(content)
        
        return str(file_path)
    
    async def create_voice_clone_from_upload(
        self,
        file: UploadFile,
        voice_id: str,
        preview_text: Optional[str] = None
    ) -> VoiceCloneJob:
        """Complete workflow to create voice clone from uploaded file"""
        
        # Validate file format
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.mp3', '.m4a', '.wav']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Supported formats: .mp3, .m4a, .wav"
            )
        
        # Save the uploaded file
        file_path = await self.save_uploaded_file(file)
        
        try:
            # Create voice clone using MCP
            job = await self.client.create_voice_clone(
                file_path=file_path,
                voice_id=voice_id,
                preview_text=preview_text
            )
            
            return job
            
        except Exception as e:
            # Clean up the uploaded file if voice cloning fails
            try:
                Path(file_path).unlink()
            except:
                pass
            raise e
    
    async def generate_speech_with_voice(
        self,
        text: str,
        voice_id: str,
        model: str = "speech-02-hd",
        speed: float = 1.0,
        emotion: str = "happy"
    ) -> str:
        """Generate speech using a cloned voice"""
        return await self.client.generate_speech(
            text=text,
            voice_id=voice_id,
            model=model,
            speed=speed,
            emotion=emotion
        )
    
    async def list_available_voices(self, voice_type: str = "all") -> List[Dict[str, Any]]:
        """List available voices"""
        return await self.client.list_voices(voice_type)
    
    async def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old audio files"""
        base_path = Path(self.client.base_path)
        current_time = datetime.now().timestamp()
        
        for file_path in base_path.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (max_age_hours * 3600):
                    try:
                        file_path.unlink()
                        logger.info(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up file {file_path}: {str(e)}")

# Global instance
voice_clone_manager = None

def get_voice_clone_manager() -> VoiceCloneManager:
    """Get or create the voice clone manager instance"""
    global voice_clone_manager
    if voice_clone_manager is None:
        voice_clone_manager = VoiceCloneManager()
    return voice_clone_manager