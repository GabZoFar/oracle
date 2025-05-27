#!/usr/bin/env python3
"""
Script d'aide à l'installation de FFmpeg pour Maître Joueur.
Ce script détecte le système d'exploitation et fournit des instructions d'installation.
"""

import platform
import subprocess
import sys
import shutil
from pathlib import Path


def check_ffmpeg():
    """Vérifie si FFmpeg est déjà installé."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg est déjà installé : {version_line}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    print("❌ FFmpeg n'est pas installé ou n'est pas dans le PATH")
    return False


def get_installation_instructions():
    """Retourne les instructions d'installation selon le système d'exploitation."""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return {
            "system": "macOS",
            "methods": [
                {
                    "name": "Homebrew (recommandé)",
                    "commands": [
                        "# Installer Homebrew si pas déjà fait :",
                        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                        "",
                        "# Installer FFmpeg :",
                        "brew install ffmpeg"
                    ],
                    "description": "Méthode la plus simple sur macOS"
                },
                {
                    "name": "MacPorts",
                    "commands": [
                        "sudo port install ffmpeg"
                    ],
                    "description": "Alternative à Homebrew"
                },
                {
                    "name": "Téléchargement direct",
                    "commands": [
                        "# Télécharger depuis : https://ffmpeg.org/download.html#build-mac",
                        "# Extraire et ajouter au PATH"
                    ],
                    "description": "Installation manuelle"
                }
            ]
        }
    
    elif system == "linux":
        return {
            "system": "Linux",
            "methods": [
                {
                    "name": "Ubuntu/Debian",
                    "commands": [
                        "sudo apt update",
                        "sudo apt install ffmpeg"
                    ],
                    "description": "Pour les distributions basées sur Debian"
                },
                {
                    "name": "CentOS/RHEL/Fedora",
                    "commands": [
                        "# CentOS/RHEL :",
                        "sudo yum install ffmpeg",
                        "",
                        "# Fedora :",
                        "sudo dnf install ffmpeg"
                    ],
                    "description": "Pour les distributions Red Hat"
                },
                {
                    "name": "Arch Linux",
                    "commands": [
                        "sudo pacman -S ffmpeg"
                    ],
                    "description": "Pour Arch Linux"
                }
            ]
        }
    
    elif system == "windows":
        return {
            "system": "Windows",
            "methods": [
                {
                    "name": "Chocolatey (recommandé)",
                    "commands": [
                        "# Installer Chocolatey si pas déjà fait (en tant qu'administrateur) :",
                        'Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))',
                        "",
                        "# Installer FFmpeg :",
                        "choco install ffmpeg"
                    ],
                    "description": "Gestionnaire de paquets pour Windows"
                },
                {
                    "name": "Winget",
                    "commands": [
                        "winget install FFmpeg"
                    ],
                    "description": "Gestionnaire de paquets Microsoft"
                },
                {
                    "name": "Téléchargement direct",
                    "commands": [
                        "# 1. Télécharger depuis : https://ffmpeg.org/download.html#build-windows",
                        "# 2. Extraire dans C:\\ffmpeg",
                        "# 3. Ajouter C:\\ffmpeg\\bin au PATH système"
                    ],
                    "description": "Installation manuelle"
                }
            ]
        }
    
    else:
        return {
            "system": "Système non reconnu",
            "methods": [
                {
                    "name": "Installation générique",
                    "commands": [
                        "# Visitez https://ffmpeg.org/download.html",
                        "# Téléchargez la version pour votre système",
                        "# Ajoutez FFmpeg à votre PATH"
                    ],
                    "description": "Instructions génériques"
                }
            ]
        }


def print_instructions():
    """Affiche les instructions d'installation."""
    print("🎬 Installation de FFmpeg pour Maître Joueur")
    print("=" * 50)
    
    if check_ffmpeg():
        print("\n🎉 FFmpeg est déjà installé ! Vous pouvez utiliser la compression automatique.")
        return
    
    instructions = get_installation_instructions()
    
    print(f"\n📱 Système détecté : {instructions['system']}")
    print("\n📋 Instructions d'installation :")
    
    for i, method in enumerate(instructions['methods'], 1):
        print(f"\n{i}. {method['name']}")
        print(f"   {method['description']}")
        print()
        for command in method['commands']:
            if command.startswith('#'):
                print(f"   {command}")
            else:
                print(f"   $ {command}")
    
    print("\n" + "=" * 50)
    print("📝 Notes importantes :")
    print("• Redémarrez votre terminal après l'installation")
    print("• Vérifiez l'installation avec : ffmpeg -version")
    print("• Relancez Maître Joueur pour activer la compression automatique")


def main():
    """Fonction principale."""
    try:
        print_instructions()
    except KeyboardInterrupt:
        print("\n\n👋 Installation annulée.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 