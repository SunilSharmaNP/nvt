#!/usr/bin/env python3
"""
Test script to verify bot setup without running the actual bot
This ensures all imports and configurations are correct
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import pyrogram
        print("✅ Pyrogram imported")
    except ImportError as e:
        print(f"❌ Pyrogram import failed: {e}")
        return False
    
    try:
        import motor
        print("✅ Motor (MongoDB) imported")
    except ImportError as e:
        print(f"❌ Motor import failed: {e}")
        return False
    
    try:
        import aiofiles
        print("✅ aiofiles imported")
    except ImportError as e:
        print("❌ aiofiles import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\n🧪 Testing FFmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg test failed")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        return False
    except Exception as e:
        print(f"❌ FFmpeg test error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    if not os.path.exists('.env'):
        print("⚠️  .env file not found (this is okay for first run)")
        print("   Run 'python setup.py' to create it")
        return True
    
    try:
        from config import Config
        print("✅ Config loaded")
        
        # Check required fields
        required = ['BOT_TOKEN', 'API_ID', 'API_HASH', 'OWNER_ID']
        missing = []
        
        if not Config.BOT_TOKEN or Config.BOT_TOKEN == "":
            missing.append('BOT_TOKEN')
        if Config.API_ID == 0:
            missing.append('API_ID')
        if not Config.API_HASH or Config.API_HASH == "":
            missing.append('API_HASH')
        if Config.OWNER_ID == 0:
            missing.append('OWNER_ID')
        
        if missing:
            print(f"⚠️  Missing configuration: {', '.join(missing)}")
            print("   Run 'python setup.py' to configure")
            return True
        else:
            print("✅ All required config fields present")
            return True
            
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_bot_structure():
    """Test bot module structure"""
    print("\n🧪 Testing bot structure...")
    
    try:
        from bot import Bot
        print("✅ Bot class can be imported")
    except Exception as e:
        print(f"❌ Bot import failed: {e}")
        return False
    
    try:
        from bot.database import db
        print("✅ Database module imported")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from bot.helpers.buttons import main_menu_buttons
        print("✅ Helper modules imported")
    except Exception as e:
        print(f"❌ Helper import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test required directories"""
    print("\n🧪 Testing directories...")
    
    required_dirs = ['bot', 'bot/plugins', 'bot/database', 'bot/helpers', 'bot/utils', 'downloads']
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"⚠️  {dir_path}/ not found, creating...")
            os.makedirs(dir_path, exist_ok=True)
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("🎬 Video Tools Bot - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("FFmpeg", test_ffmpeg),
        ("Configuration", test_config),
        ("Bot Structure", test_bot_structure),
        ("Directories", test_directories)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Bot is ready to configure and run.")
        print("\nNext steps:")
        print("1. Run 'python setup.py' to configure")
        print("2. Run 'python main.py' to start the bot")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)
