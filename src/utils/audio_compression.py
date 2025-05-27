"""Audio compression utilities and recommendations."""

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tempfile
import os

logger = logging.getLogger(__name__)


class AudioCompressionHelper:
    """Helper class for audio compression recommendations and utilities."""
    
    def __init__(self):
        """Initialize the compression helper."""
        self.ffmpeg_available = self._check_ffmpeg_availability()
    
    def _check_ffmpeg_availability(self) -> bool:
        """Check if FFmpeg is available on the system."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available for compression."""
        return self.ffmpeg_available
    
    def compress_audio_file(
        self, 
        input_path: Path, 
        output_path: Optional[Path] = None,
        target_bitrate: int = 128,
        target_format: str = "mp3",
        mono: bool = False,
        sample_rate: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Compress an audio file using FFmpeg.
        
        Args:
            input_path: Path to the input audio file
            output_path: Path for the output file (optional, will generate if None)
            target_bitrate: Target bitrate in kbps
            target_format: Target format (mp3, wav, etc.)
            mono: Convert to mono
            sample_rate: Target sample rate (optional)
            
        Returns:
            Tuple of (success, message, output_path)
        """
        if not self.ffmpeg_available:
            return False, "FFmpeg n'est pas disponible sur ce système", None
        
        try:
            # Generate output path if not provided
            if output_path is None:
                input_stem = input_path.stem
                output_path = input_path.parent / f"{input_stem}_compressed.{target_format}"
            
            # Build FFmpeg command
            cmd = ["ffmpeg", "-i", str(input_path)]
            
            # Audio codec and bitrate
            if target_format.lower() == "mp3":
                cmd.extend(["-codec:a", "libmp3lame", "-b:a", f"{target_bitrate}k"])
            elif target_format.lower() == "wav":
                cmd.extend(["-codec:a", "pcm_s16le"])
            else:
                cmd.extend(["-b:a", f"{target_bitrate}k"])
            
            # Mono conversion
            if mono:
                cmd.extend(["-ac", "1"])
            
            # Sample rate
            if sample_rate:
                cmd.extend(["-ar", str(sample_rate)])
            
            # Overwrite output file and add output path
            cmd.extend(["-y", str(output_path)])
            
            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Check if output file was created and has reasonable size
                if output_path.exists() and output_path.stat().st_size > 1000:  # At least 1KB
                    output_size_mb = output_path.stat().st_size / (1024 * 1024)
                    input_size_mb = input_path.stat().st_size / (1024 * 1024)
                    reduction_percent = ((input_size_mb - output_size_mb) / input_size_mb) * 100
                    
                    message = f"Compression réussie ! Taille réduite de {input_size_mb:.1f} MB à {output_size_mb:.1f} MB ({reduction_percent:.1f}% de réduction)"
                    return True, message, output_path
                else:
                    return False, "Le fichier compressé n'a pas été créé correctement", None
            else:
                error_msg = result.stderr if result.stderr else "Erreur inconnue"
                return False, f"Erreur FFmpeg: {error_msg}", None
                
        except subprocess.TimeoutExpired:
            return False, "La compression a pris trop de temps (timeout)", None
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            return False, f"Erreur lors de la compression: {str(e)}", None
    
    def get_optimal_compression_settings(self, file_size_mb: float, file_format: str) -> Dict[str, any]:
        """
        Get optimal compression settings based on file size and format.
        
        Args:
            file_size_mb: Current file size in MB
            file_format: Current file format
            
        Returns:
            Dictionary with optimal settings
        """
        settings = {
            "target_format": "mp3",
            "target_bitrate": 128,
            "mono": False,
            "sample_rate": None,
            "estimated_size_mb": 0
        }
        
        # Adjust settings based on file size
        if file_size_mb > 100:
            # Very large files - aggressive compression
            settings.update({
                "target_bitrate": 96,
                "mono": True,
                "sample_rate": 22050
            })
        elif file_size_mb > 50:
            # Large files - moderate compression
            settings.update({
                "target_bitrate": 128,
                "mono": True
            })
        elif file_size_mb > 25:
            # Medium files - light compression
            settings.update({
                "target_bitrate": 128
            })
        
        # Estimate compressed size
        settings["estimated_size_mb"] = self.estimate_compressed_size(
            file_size_mb, 
            file_format, 
            settings["target_format"], 
            settings["target_bitrate"]
        )
        
        # Adjust if still too large
        if settings["estimated_size_mb"] > 24:
            settings.update({
                "target_bitrate": 64,
                "mono": True,
                "sample_rate": 22050
            })
            settings["estimated_size_mb"] = self.estimate_compressed_size(
                file_size_mb, 
                file_format, 
                settings["target_format"], 
                settings["target_bitrate"]
            )
        
        return settings
    
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
            "Compression automatique FFmpeg (dans l'app)",
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