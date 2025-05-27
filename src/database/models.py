"""Database models for the RPG Session Management Tool."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Session(Base):
    """Model for RPG session data."""
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Session metadata
    title = Column(String(255), nullable=False)
    session_number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # File information
    audio_file_path = Column(String(500), nullable=False)
    audio_file_name = Column(String(255), nullable=False)
    audio_file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Transcription and analysis
    transcript = Column(Text, nullable=True)
    narrative_summary = Column(Text, nullable=True)
    tldr_summary = Column(Text, nullable=True)
    
    # Structured data (stored as JSON)
    npcs = Column(JSON, nullable=True, default=list)  # List of NPC names
    items = Column(JSON, nullable=True, default=list)  # List of items found
    locations = Column(JSON, nullable=True, default=list)  # List of locations visited
    key_events = Column(JSON, nullable=True, default=list)  # List of key events
    
    # User notes and comments
    comments = Column(Text, nullable=True)
    
    # Processing status
    processing_status = Column(String(50), nullable=False, default="uploaded")
    # Status values: uploaded, transcribing, analyzing, completed, error
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, title='{self.title}', session_number={self.session_number})>"
    
    def to_dict(self) -> dict:
        """Convert the session to a dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "session_number": self.session_number,
            "date": self.date.isoformat() if self.date else None,
            "audio_file_path": self.audio_file_path,
            "audio_file_name": self.audio_file_name,
            "audio_file_size": self.audio_file_size,
            "transcript": self.transcript,
            "narrative_summary": self.narrative_summary,
            "tldr_summary": self.tldr_summary,
            "npcs": self.npcs or [],
            "items": self.items or [],
            "locations": self.locations or [],
            "key_events": self.key_events or [],
            "comments": self.comments,
            "processing_status": self.processing_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Campaign(Base):
    """Model for campaign information (future enhancement)."""
    
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    game_system = Column(String(100), nullable=True)  # D&D 5e, Pathfinder, etc.
    
    # Campaign metadata
    start_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="active")  # active, completed, paused
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name='{self.name}', system='{self.game_system}')>" 