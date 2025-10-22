#!/usr/bin/env python3
"""
Setup script for Video Tools Bot
This script helps configure the bot for first-time use
"""

import os
import sys

def create_env_file():
    """Create .env file with user input"""
    print("🎬 Video Tools Bot - Setup Wizard\n")
    print("=" * 50)
    
    if os.path.exists(".env"):
        response = input("\n.env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📝 Please provide the following information:\n")
    
    # Bot Configuration
    print("1️⃣ Telegram Bot Configuration")
    bot_token = input("   BOT_TOKEN (from @BotFather): ").strip()
    api_id = input("   API_ID (from my.telegram.org): ").strip()
    api_hash = input("   API_HASH (from my.telegram.org): ").strip()
    
    # Owner Configuration
    print("\n2️⃣ Bot Owner Configuration")
    owner_id = input("   OWNER_ID (your Telegram user ID): ").strip()
    sudo_users = input("   SUDO_USERS (comma-separated IDs, or press Enter to skip): ").strip()
    
    # Authorized Groups
    print("\n3️⃣ Authorized Groups")
    print("   Get group IDs by adding @userinfobot to your group")
    authorized_groups = input("   AUTHORIZED_GROUPS (comma-separated group IDs): ").strip()
    
    # MongoDB Configuration
    print("\n4️⃣ MongoDB Configuration")
    print("   You can use MongoDB Atlas (free): https://www.mongodb.com/cloud/atlas/register")
    mongo_uri = input("   MONGO_URI (default: mongodb://localhost:27017): ").strip()
    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017"
    
    database_name = input("   DATABASE_NAME (default: video_tools_bot): ").strip()
    if not database_name:
        database_name = "video_tools_bot"
    
    # Optional Configuration
    print("\n5️⃣ Optional Configuration")
    gofile_api = input("   GOFILE_API_KEY (press Enter to skip): ").strip()
    log_channel = input("   LOG_CHANNEL (channel ID for logs, press Enter to skip): ").strip()
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration
BOT_TOKEN={bot_token}
API_ID={api_id}
API_HASH={api_hash}

# Bot Owner/Admin Configuration
OWNER_ID={owner_id}
SUDO_USERS={sudo_users}

# Authorized Groups (comma-separated group IDs)
AUTHORIZED_GROUPS={authorized_groups}

# MongoDB Configuration
MONGO_URI={mongo_uri}
DATABASE_NAME={database_name}

# Download/Upload Configuration
DOWNLOAD_DIR=downloads
MAX_FILE_SIZE=2147483648

# GoFile Configuration (Optional)
GOFILE_API_KEY={gofile_api}

# FFmpeg Configuration
FFMPEG_THREADS=2

# Bot Settings
SESSION_NAME=video_tools_bot
LOG_CHANNEL={log_channel}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n✅ Configuration saved to .env file!")
    print("\n📋 Next steps:")
    print("   1. Make sure MongoDB is running")
    print("   2. Install FFmpeg if not already installed")
    print("   3. Run: python main.py")
    print("\n🎬 Your Video Tools Bot is ready to launch!")

if __name__ == "__main__":
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
