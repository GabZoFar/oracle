"""AI analysis service for extracting RPG session information."""

import logging
import json
from typing import Dict, Any, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

import openai
from openai import OpenAI
from pydantic import BaseModel, Field

from ..config import settings

logger = logging.getLogger(__name__)


class RPGSessionAnalysis(BaseModel):
    """Structured model for RPG session analysis results."""
    
    narrative_summary: str = Field(..., description="2-5 paragraph narrative summary of the session")
    tldr_summary: str = Field(..., description="Short TL;DR summary for session start")
    npcs: List[str] = Field(default_factory=list, description="List of NPCs encountered")
    items: List[str] = Field(default_factory=list, description="List of items found or mentioned")
    locations: List[str] = Field(default_factory=list, description="List of locations visited")
    key_events: List[str] = Field(default_factory=list, description="List of key events that occurred")
    session_title: str = Field(..., description="Suggested title for the session")


class AIAnalysisService:
    """Service for analyzing RPG session transcripts using AI."""
    
    def __init__(self):
        """Initialize the AI analysis service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _create_analysis_prompt(self, transcript: str) -> str:
        """
        Create a structured prompt for analyzing the RPG session transcript.
        
        Args:
            transcript: The session transcript to analyze
            
        Returns:
            Formatted prompt for the AI
        """
        return f"""
Analyse cette transcription d'une session de jeu de rôle et extrais les informations suivantes :

TRANSCRIPTION:
{transcript}

Fournis une analyse structurée au format JSON avec les champs suivants :

1. "narrative_summary": Un résumé narratif de 2-5 paragraphes décrivant ce qui s'est passé pendant la session, écrit comme une histoire engageante.

2. "tldr_summary": Un résumé très court (1-2 phrases) type "TL;DR" qui peut être lu au début de la prochaine session pour rappeler où on en était.

3. "npcs": Une liste des PNJ (Personnages Non-Joueurs) rencontrés ou mentionnés pendant la session.

4. "items": Une liste des objets trouvés, achetés, utilisés ou mentionnés pendant la session.

5. "locations": Une liste des lieux visités ou mentionnés pendant la session.

6. "key_events": Une liste des événements clés qui se sont produits (combats, découvertes importantes, décisions majeures, etc.).

7. "session_title": Un titre accrocheur pour cette session qui capture l'essence de ce qui s'est passé.

Réponds uniquement avec du JSON valide, sans texte supplémentaire.
"""
    
    def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze a transcript using OpenAI GPT.
        
        Args:
            transcript: The session transcript to analyze
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            Exception: If analysis fails
        """
        try:
            logger.info("Starting AI analysis of transcript")
            
            prompt = self._create_analysis_prompt(transcript)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using latest GPT-4 model
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un assistant spécialisé dans l'analyse de sessions de jeu de rôle. Tu extrais des informations structurées des transcriptions de sessions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=2000,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse the JSON response
            analysis_text = response.choices[0].message.content
            analysis_data = json.loads(analysis_text)
            
            # Validate using Pydantic model
            validated_analysis = RPGSessionAnalysis(**analysis_data)
            
            result = {
                "narrative_summary": validated_analysis.narrative_summary,
                "tldr_summary": validated_analysis.tldr_summary,
                "npcs": validated_analysis.npcs,
                "items": validated_analysis.items,
                "locations": validated_analysis.locations,
                "key_events": validated_analysis.key_events,
                "session_title": validated_analysis.session_title,
                "status": "completed"
            }
            
            logger.info("AI analysis completed successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise Exception(f"AI analysis failed: Invalid JSON response")
        except openai.APIError as e:
            logger.error(f"OpenAI API error during analysis: {e}")
            raise Exception(f"AI analysis failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during AI analysis: {e}")
            raise Exception(f"AI analysis failed: {e}")
    
    async def analyze_transcript_async(self, transcript: str) -> Dict[str, Any]:
        """
        Asynchronously analyze a transcript.
        
        Args:
            transcript: The session transcript to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.analyze_transcript,
            transcript
        )
    
    def generate_session_title(self, transcript: str) -> str:
        """
        Generate a catchy title for the session based on the transcript.
        
        Args:
            transcript: The session transcript
            
        Returns:
            Generated session title
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu génères des titres accrocheurs pour des sessions de jeu de rôle basés sur leur contenu."
                    },
                    {
                        "role": "user",
                        "content": f"Génère un titre court et accrocheur pour cette session de JDR :\n\n{transcript[:1000]}..."
                    }
                ],
                temperature=0.7,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip().strip('"')
            
        except Exception as e:
            logger.error(f"Failed to generate session title: {e}")
            return "Session sans titre"
    
    def validate_transcript_length(self, transcript: str) -> bool:
        """
        Validate that the transcript is long enough for meaningful analysis.
        
        Args:
            transcript: The transcript to validate
            
        Returns:
            True if transcript is valid for analysis
        """
        if not transcript or len(transcript.strip()) < 100:
            logger.warning("Transcript too short for meaningful analysis")
            return False
        return True


# Global AI analysis service instance
ai_analysis_service = AIAnalysisService() 