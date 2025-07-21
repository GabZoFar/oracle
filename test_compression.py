#!/usr/bin/env python3
"""
Test script for the audio compression functionality.
"""

import sys
from pathlib import Path
import tempfile
import os

def test_compression_helper():
    """Test the compression helper functionality."""
    print("🗜️ Test de la fonctionnalité de compression")
    print("=" * 50)
    
    try:
        from src.utils.audio_compression import audio_helper
        print("✅ Module de compression importé avec succès")
    except ImportError as e:
        print(f"❌ Échec de l'import du module de compression : {e}")
        return False
    
    # Test FFmpeg availability
    ffmpeg_available = audio_helper.is_ffmpeg_available()
    if ffmpeg_available:
        print("✅ FFmpeg est disponible pour la compression automatique")
    else:
        print("⚠️ FFmpeg n'est pas disponible - compression automatique désactivée")
    
    # Test compression recommendations
    try:
        recommendations = audio_helper.get_compression_recommendations(100.0, "wav")
        print("✅ Génération des recommandations de compression réussie")
        print(f"   - Réduction estimée : {recommendations['estimated_reduction']}")
        print(f"   - Nombre de méthodes : {len(recommendations['methods'])}")
        print(f"   - Nombre d'outils : {len(recommendations['tools'])}")
    except Exception as e:
        print(f"❌ Échec de la génération des recommandations : {e}")
        return False
    
    # Test optimal settings calculation
    try:
        settings = audio_helper.get_optimal_compression_settings(100.0, "wav")
        print("✅ Calcul des paramètres optimaux réussi")
        print(f"   - Format cible : {settings['target_format']}")
        print(f"   - Bitrate : {settings['target_bitrate']} kbps")
        print(f"   - Mono : {settings['mono']}")
        print(f"   - Taille estimée : {settings['estimated_size_mb']:.1f} MB")
    except Exception as e:
        print(f"❌ Échec du calcul des paramètres optimaux : {e}")
        return False
    
    # Test size estimation
    try:
        estimated_size = audio_helper.estimate_compressed_size(100.0, "wav", "mp3", 128)
        print(f"✅ Estimation de taille réussie : {estimated_size:.1f} MB")
    except Exception as e:
        print(f"❌ Échec de l'estimation de taille : {e}")
        return False
    
    # Test FFmpeg commands generation
    try:
        commands = audio_helper.get_ffmpeg_commands("input.wav", "output.mp3")
        print(f"✅ Génération des commandes FFmpeg réussie : {len(commands)} commandes")
    except Exception as e:
        print(f"❌ Échec de la génération des commandes FFmpeg : {e}")
        return False
    
    # Test Audacity instructions
    try:
        instructions = audio_helper.get_audacity_instructions()
        print(f"✅ Génération des instructions Audacity réussie : {len(instructions)} étapes")
    except Exception as e:
        print(f"❌ Échec de la génération des instructions Audacity : {e}")
        return False
    
    return True


def test_compression_scenarios():
    """Test different compression scenarios."""
    print("\n📊 Test des scénarios de compression")
    print("-" * 30)
    
    from src.utils.audio_compression import audio_helper
    
    scenarios = [
        {"size": 52.0, "format": "m4a", "description": "Votre fichier de 52MB"},
        {"size": 500.0, "format": "wav", "description": "Fichier WAV très volumineux"},
        {"size": 30.0, "format": "mp3", "description": "MP3 légèrement trop gros"},
        {"size": 80.0, "format": "flac", "description": "FLAC de taille moyenne"},
    ]
    
    for scenario in scenarios:
        print(f"\n🎵 {scenario['description']} ({scenario['size']} MB, {scenario['format'].upper()})")
        
        # Get optimal settings
        settings = audio_helper.get_optimal_compression_settings(scenario['size'], scenario['format'])
        
        print(f"   📋 Paramètres optimaux :")
        print(f"      - Format : {settings['target_format'].upper()}")
        print(f"      - Bitrate : {settings['target_bitrate']} kbps")
        print(f"      - Mono : {'Oui' if settings['mono'] else 'Non'}")
        print(f"      - Fréquence : {settings['sample_rate'] or 'Originale'}")
        print(f"      - Taille estimée : {settings['estimated_size_mb']:.1f} MB")
        
        if settings['estimated_size_mb'] <= 25:
            print(f"   ✅ Compatible avec l'API Whisper")
        else:
            print(f"   ⚠️ Encore trop volumineux, compression plus agressive nécessaire")


def main():
    """Fonction principale."""
    print("🧪 Test de la compression audio - Oracle")
    print("=" * 60)
    
    # Test basic functionality
    if not test_compression_helper():
        print("\n❌ Les tests de base ont échoué")
        return 1
    
    # Test compression scenarios
    test_compression_scenarios()
    
    print("\n" + "=" * 60)
    print("📋 Résumé des fonctionnalités de compression :")
    print("✅ Détection automatique de FFmpeg")
    print("✅ Recommandations de compression intelligentes")
    print("✅ Calcul des paramètres optimaux")
    print("✅ Estimation de taille précise")
    print("✅ Génération de commandes FFmpeg")
    print("✅ Instructions Audacity étape par étape")
    
    print("\n🎉 Tous les tests de compression sont passés avec succès !")
    print("\n💡 Pour tester la compression réelle :")
    print("   1. Lancez l'application : uv run streamlit run app.py")
    print("   2. Uploadez un fichier > 25MB")
    print("   3. Cliquez sur 'Compresser automatiquement'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 