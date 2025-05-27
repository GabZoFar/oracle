"""Audio transcription service using OpenAI Whisper."""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

import openai
from openai import OpenAI

from ..config import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper."""
    
    def __init__(self):
        """Initialize the transcription service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def transcribe_audio(self, audio_file_path: Path) -> Dict[str, Any]:
        """
        Transcribe an audio file using OpenAI Whisper.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing transcript and metadata
            
        Raises:
            Exception: If transcription fails
        """
        try:
            logger.info(f"Starting transcription for {audio_file_path}")
            
            # Check file size and warn if it's very large
            file_size_mb = audio_file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 100:
                logger.warning(f"Large file detected: {file_size_mb:.2f} MB. This may take longer to process.")
            
            with open(audio_file_path, "rb") as audio_file:
                # Use Whisper API for transcription
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",  # Get timestamps and metadata
                    language="fr",  # French for RPG sessions, change as needed
                    # Add timeout for large files
                    timeout=600 if file_size_mb > 100 else 300  # 10 min for large files, 5 min for smaller
                )
            
            result = {
                "transcript": response.text,
                "language": getattr(response, 'language', 'unknown'),
                "duration": getattr(response, 'duration', None),
                "segments": getattr(response, 'segments', []),
                "file_size_mb": file_size_mb,
                "status": "completed"
            }
            
            logger.info(f"Transcription completed for {audio_file_path}. Duration: {result.get('duration', 'unknown')} seconds")
            return result
            
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI API timeout during transcription: {e}")
            raise Exception(f"Transcription timed out. Large files may take longer. Please try again or split the file into smaller segments.")
        except openai.APIError as e:
            logger.error(f"OpenAI API error during transcription: {e}")
            # Check if it's a file size error
            if "file size" in str(e).lower() or "too large" in str(e).lower():
                raise Exception(f"File too large for Whisper API. Maximum size is 25MB. Please compress or split your file.")
            raise Exception(f"Transcription failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}")
            raise Exception(f"Transcription failed: {e}")
    
    async def transcribe_audio_async(self, audio_file_path: Path) -> Dict[str, Any]:
        """
        Asynchronously transcribe an audio file.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing transcript and metadata
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.transcribe_audio, 
            audio_file_path
        )
    
    def validate_audio_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Validate that the audio file is supported and accessible.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not file_path.exists():
                error_msg = f"Audio file does not exist: {file_path}"
                logger.error(error_msg)
                return False, error_msg
            
            # Check file extension
            file_extension = file_path.suffix.lower().lstrip('.')
            if file_extension not in settings.supported_audio_formats:
                error_msg = f"Unsupported audio format: {file_extension}. Supported: {', '.join(settings.supported_audio_formats)}"
                logger.error(error_msg)
                return False, error_msg
            
            # Check file size
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size > settings.max_file_size_bytes:
                error_msg = f"File too large: {file_size_mb:.2f} MB. Maximum allowed: {settings.max_file_size_mb} MB"
                logger.error(error_msg)
                return False, error_msg
            
            if file_size == 0:
                error_msg = f"File is empty: {file_path}"
                logger.error(error_msg)
                return False, error_msg
            
            # Warn about Whisper API limits (25MB)
            if file_size_mb > 25:
                warning_msg = f"⚠️ File is {file_size_mb:.2f} MB. OpenAI Whisper API has a 25MB limit. You may need to compress the file."
                logger.warning(warning_msg)
                return False, warning_msg
            
            return True, "File is valid"
            
        except Exception as e:
            error_msg = f"Error validating audio file {file_path}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats."""
        return settings.supported_audio_formats.copy()
    
    def estimate_processing_time(self, file_size_mb: float) -> str:
        """
        Estimate processing time based on file size.
        
        Args:
            file_size_mb: File size in megabytes
            
        Returns:
            Estimated processing time as a string
        """
        # Rough estimates based on typical processing times
        if file_size_mb < 10:
            return "1-2 minutes"
        elif file_size_mb < 25:
            return "2-5 minutes"
        elif file_size_mb < 50:
            return "5-10 minutes"
        else:
            return "10+ minutes"


# Global transcription service instance
transcription_service = TranscriptionService() 