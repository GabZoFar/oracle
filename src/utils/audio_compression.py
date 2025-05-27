"""Audio compression utilities and recommendations."""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class AudioCompressionHelper:
    """Helper class for audio compression recommendations and utilities."""
    
    @staticmethod
    def get_compression_recommendations(file_size_mb: float, file_format: str) -> Dict[str, str]:
        """
        Get compression recommendations based on file size and format.
        
        Args:
            file_size_mb: Current file size in MB
            file_format: Current file format (mp3, wav, etc.)
            
        Returns:
            Dictionary with compression recommendations
        """
        recommendations = {
            "current_size": f"{file_size_mb:.2f} MB",
            "target_size": "< 25 MB",
            "methods": [],
            "tools": [],
            "estimated_reduction": ""
        }
        
        # Format-specific recommendations
        if file_format.lower() == "wav":
            recommendations["methods"].extend([
                "Convertir en MP3 (réduction ~90%)",
                "Réduire la qualité d'échantillonnage (44.1kHz → 22kHz)",
                "Convertir en mono si stéréo (réduction ~50%)"
            ])
            recommendations["estimated_reduction"] = "80-90%"
            
        elif file_format.lower() == "flac":
            recommendations["methods"].extend([
                "Convertir en MP3 (réduction ~70%)",
                "Réduire le bitrate (320kbps → 128kbps)",
                "Convertir en mono si stéréo"
            ])
            recommendations["estimated_reduction"] = "60-80%"
            
        elif file_format.lower() == "m4a":
            recommendations["methods"].extend([
                "Réduire le bitrate (256kbps → 128kbps)",
                "Convertir en MP3",
                "Réduire la fréquence d'échantillonnage"
            ])
            recommendations["estimated_reduction"] = "40-60%"
            
        else:  # MP3 and others
            recommendations["methods"].extend([
                "Réduire le bitrate (320kbps → 128kbps ou 96kbps)",
                "Convertir en mono si stéréo",
                "Couper les silences au début/fin"
            ])
            recommendations["estimated_reduction"] = "30-50%"
        
        # Add general tools
        recommendations["tools"] = [
            "Audacity (gratuit, interface graphique)",
            "FFmpeg (ligne de commande, très puissant)",
            "Online Audio Converter",
            "VLC Media Player (conversion simple)",
            "HandBrake (pour formats vidéo avec audio)"
        ]
        
        return recommendations
    
    @staticmethod
    def get_ffmpeg_commands(input_file: str, output_file: str, target_size_mb: float = 25) -> List[str]:
        """
        Generate FFmpeg commands for audio compression.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            target_size_mb: Target file size in MB
            
        Returns:
            List of FFmpeg command strings
        """
        commands = []
        
        # Basic MP3 conversion with different quality levels
        commands.extend([
            f'ffmpeg -i "{input_file}" -codec:a libmp3lame -b:a 128k "{output_file}"',
            f'ffmpeg -i "{input_file}" -codec:a libmp3lame -b:a 96k "{output_file}"',
            f'ffmpeg -i "{input_file}" -codec:a libmp3lame -b:a 64k "{output_file}"'
        ])
        
        # Convert to mono
        commands.append(
            f'ffmpeg -i "{input_file}" -codec:a libmp3lame -ac 1 -b:a 128k "{output_file}"'
        )
        
        # Reduce sample rate
        commands.append(
            f'ffmpeg -i "{input_file}" -codec:a libmp3lame -ar 22050 -b:a 128k "{output_file}"'
        )
        
        return commands
    
    @staticmethod
    def get_audacity_instructions() -> List[str]:
        """Get step-by-step Audacity compression instructions."""
        return [
            "1. Ouvrir Audacity et importer votre fichier audio",
            "2. Sélectionner tout l'audio (Ctrl+A)",
            "3. Aller dans Pistes → Mixer et rendre → Mixer et rendre",
            "4. Si stéréo, aller dans Pistes → Mixer → Convertir en mono",
            "5. Aller dans Fichier → Exporter → Exporter en MP3",
            "6. Choisir une qualité de 128 kbps ou moins",
            "7. Cliquer sur Enregistrer"
        ]
    
    @staticmethod
    def estimate_compressed_size(original_size_mb: float, original_format: str, target_format: str = "mp3", bitrate: int = 128) -> float:
        """
        Estimate compressed file size.
        
        Args:
            original_size_mb: Original file size in MB
            original_format: Original format
            target_format: Target format
            bitrate: Target bitrate in kbps
            
        Returns:
            Estimated compressed size in MB
        """
        # Rough compression ratios based on format conversion
        compression_ratios = {
            ("wav", "mp3"): 0.1,  # WAV to MP3 is ~90% reduction
            ("flac", "mp3"): 0.3,  # FLAC to MP3 is ~70% reduction
            ("m4a", "mp3"): 0.6,   # M4A to MP3 is ~40% reduction
            ("mp3", "mp3"): 0.7,   # MP3 to lower quality MP3
        }
        
        ratio = compression_ratios.get((original_format.lower(), target_format.lower()), 0.5)
        
        # Adjust based on bitrate (128kbps is baseline)
        bitrate_factor = bitrate / 128
        
        estimated_size = original_size_mb * ratio * bitrate_factor
        return max(estimated_size, 1.0)  # Minimum 1MB
    
    @staticmethod
    def should_split_file(file_size_mb: float, max_segment_mb: float = 20) -> Tuple[bool, int]:
        """
        Determine if file should be split and into how many parts.
        
        Args:
            file_size_mb: File size in MB
            max_segment_mb: Maximum size per segment
            
        Returns:
            Tuple of (should_split, number_of_segments)
        """
        if file_size_mb <= max_segment_mb:
            return False, 1
        
        num_segments = int(file_size_mb / max_segment_mb) + 1
        return True, num_segments
    
    @staticmethod
    def get_splitting_instructions(duration_minutes: float, num_segments: int) -> List[str]:
        """
        Get instructions for splitting audio files.
        
        Args:
            duration_minutes: Total duration in minutes
            num_segments: Number of segments to create
            
        Returns:
            List of instruction strings
        """
        segment_duration = duration_minutes / num_segments
        
        instructions = [
            f"Diviser le fichier en {num_segments} segments de ~{segment_duration:.1f} minutes chacun:",
            "",
            "**Avec Audacity:**",
            "1. Ouvrir le fichier dans Audacity",
            "2. Utiliser l'outil de sélection pour marquer chaque segment",
            "3. Sélectionner le premier segment (0 à {:.1f} min)".format(segment_duration),
            "4. Aller dans Fichier → Exporter → Exporter la sélection en MP3",
            "5. Répéter pour chaque segment",
            "",
            "**Avec FFmpeg:**"
        ]
        
        # Add FFmpeg commands for each segment
        for i in range(num_segments):
            start_time = i * segment_duration * 60  # Convert to seconds
            instructions.append(
                f'ffmpeg -i "input.wav" -ss {start_time:.0f} -t {segment_duration*60:.0f} -c copy "segment_{i+1}.wav"'
            )
        
        return instructions


# Global helper instance
audio_helper = AudioCompressionHelper() 