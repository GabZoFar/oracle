"""Configuration management for the RPG Session Management Tool."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    mistral_api_key: Optional[str] = Field(None, env="MISTRAL_API_KEY")
    
    # Database Configuration
    database_url: str = Field("sqlite:///data/sessions.db", env="DATABASE_URL")
    
    # File Upload Configuration
    upload_dir: str = Field("data/audio", env="UPLOAD_DIR")
    max_file_size_mb: int = Field(500, env="MAX_FILE_SIZE_MB")
    
    # Application Configuration
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Supported audio formats
    supported_audio_formats: list[str] = ["mp3", "wav", "m4a", "flac", "ogg"]
    
    # Large file handling
    chunk_size_mb: int = Field(25, env="CHUNK_SIZE_MB")
    enable_streaming: bool = Field(True, env="ENABLE_STREAMING")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    @property
    def upload_path(self) -> Path:
        """Get the upload directory as a Path object."""
        return Path(self.upload_dir)
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get the maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def chunk_size_bytes(self) -> int:
        """Get the chunk size in bytes for large file processing."""
        return self.chunk_size_mb * 1024 * 1024
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.upload_path.mkdir(parents=True, exist_ok=True)
        Path("data/exports").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings() 