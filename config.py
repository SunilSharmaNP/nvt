import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Configuration
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Safe int conversion with default
    try:
        API_ID = int(os.environ.get("API_ID", "0"))
    except ValueError:
        API_ID = 0
    
    API_HASH = os.environ.get("API_HASH", "")
    
    # Bot Owner/Admin Configuration
    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    except ValueError:
        OWNER_ID = 0
    
    # Parse sudo users safely
    SUDO_USERS = []
    sudo_users_str = os.environ.get("SUDO_USERS", "")
    if sudo_users_str:
        for x in sudo_users_str.split(","):
            try:
                if x.strip():
                    SUDO_USERS.append(int(x.strip()))
            except ValueError:
                pass
    
    # Parse authorized groups safely
    AUTHORIZED_GROUPS = []
    auth_groups_str = os.environ.get("AUTHORIZED_GROUPS", "")
    if auth_groups_str:
        for x in auth_groups_str.split(","):
            try:
                if x.strip():
                    AUTHORIZED_GROUPS.append(int(x.strip()))
            except ValueError:
                pass
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "video_tools_bot")
    
    # Download/Upload Configuration
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", "2147483648"))
    
    # GoFile Configuration
    GOFILE_API_KEY = os.environ.get("GOFILE_API_KEY", "")
    
    # FFmpeg Configuration
    FFMPEG_THREADS = int(os.environ.get("FFMPEG_THREADS", "2"))
    
    # Bot Settings
    SESSION_NAME = os.environ.get("SESSION_NAME", "video_tools_bot")
    LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "")
    
    # Default User Settings
    DEFAULT_SETTINGS = {
        "send_as": "document",
        "thumbnail": None,
        "filename": "default",
        "metadata": False,
        "download_mode": "telegram",
        "upload_mode": "telegram"
    }
    
    # Video Quality Presets
    VIDEO_PRESETS = {
        "1080p": {
            "resolution": "1920x1080",
            "crf": 23,
            "bitrate": "5000k",
            "audio_bitrate": "192k",
            "preset": "medium",
            "codec": "libx264"
        },
        "1080p_hevc": {
            "resolution": "1920x1080",
            "crf": 28,
            "bitrate": "3500k",
            "audio_bitrate": "192k",
            "preset": "medium",
            "codec": "libx265"
        },
        "720p": {
            "resolution": "1280x720",
            "crf": 23,
            "bitrate": "3000k",
            "audio_bitrate": "128k",
            "preset": "medium",
            "codec": "libx264"
        },
        "720p_hevc": {
            "resolution": "1280x720",
            "crf": 28,
            "bitrate": "2000k",
            "audio_bitrate": "128k",
            "preset": "medium",
            "codec": "libx265"
        },
        "480p": {
            "resolution": "854x480",
            "crf": 23,
            "bitrate": "1500k",
            "audio_bitrate": "128k",
            "preset": "medium",
            "codec": "libx264"
        },
        "480p_hevc": {
            "resolution": "854x480",
            "crf": 28,
            "bitrate": "1000k",
            "audio_bitrate": "128k",
            "preset": "medium",
            "codec": "libx265"
        },
        "360p": {
            "resolution": "640x360",
            "crf": 23,
            "bitrate": "800k",
            "audio_bitrate": "96k",
            "preset": "medium",
            "codec": "libx264"
        }
    }
