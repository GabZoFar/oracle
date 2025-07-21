#!/usr/bin/env python3
"""
Simple test script to verify the RPG Session Management Tool setup.
Run this to check if all components are properly configured.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False
    
    try:
        from src.config import settings
        print("✅ Configuration module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False
    
    try:
        from src.database.models import Session
        print("✅ Database models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database models: {e}")
        return False
    
    try:
        from src.services.transcription import transcription_service
        print("✅ Transcription service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import transcription service: {e}")
        return False
    
    try:
        from src.services.ai_analysis import ai_analysis_service
        print("✅ AI analysis service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI analysis service: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist."""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        "src",
        "src/database",
        "src/services",
        "src/components",
        "src/utils",
        "data",
        "data/audio",
        "data/exports",
        "tests"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            all_exist = False
    
    return all_exist

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.config import settings
        
        # Test that we can access configuration
        print(f"✅ Upload directory: {settings.upload_dir}")
        print(f"✅ Max file size: {settings.max_file_size_mb} MB")
        print(f"✅ Supported formats: {', '.join(settings.supported_audio_formats)}")
        
        # Check if API key is configured (without displaying it)
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            print("✅ OpenAI API key is configured")
        else:
            print("⚠️ OpenAI API key not configured (add to .env file)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\n🗄️ Testing database...")
    
    try:
        from src.database.database import init_database
        
        # Initialize database
        init_database()
        print("✅ Database initialized successfully")
        
        # Test database connection
        from src.database.database import get_db_session
        with get_db_session() as db:
            print("✅ Database connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎲 Oracle - Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Directory Tests", test_directories),
        ("Configuration Tests", test_configuration),
        ("Database Tests", test_database),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo start the application, run:")
        print("uv run streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 