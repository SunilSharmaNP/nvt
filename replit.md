# Video Tools Bot - Project Documentation

## Overview
Professional Telegram bot for advanced video processing with multiple tools including encoding, merging, conversion, watermarking, trimming, sample generation, and mediainfo extraction.

## Recent Changes (October 22, 2025)
- Complete bot implementation with all requested features
- Database models for user settings and task management
- FFmpeg integration for video processing
- Authorization system with hold/active mode for groups
- Private chat restrictions with admin override
- Full user settings system (6 configurable options)
- 7 video processing tools implemented
- Setup scripts and comprehensive documentation created

## Project Architecture

### Core Structure
```
video-tools-bot/
├── bot/                    # Main bot package
│   ├── __init__.py        # Bot client initialization
│   ├── database/          # MongoDB database layer
│   ├── helpers/           # Helper modules (FFmpeg, download, upload, buttons)
│   ├── plugins/           # Command and callback handlers
│   └── utils/             # Utility functions
├── downloads/             # Temporary file storage
├── config.py              # Configuration management
├── main.py                # Bot entry point
└── requirements.txt       # Python dependencies
```

### Key Features Implemented
1. **Authorization System**
   - Hold/Active mode toggle in authorized groups
   - Private chat restrictions (menu-only, tasks blocked)
   - Admin override for full private chat access

2. **User Settings (6 Options)**
   - Send as: Document/Video
   - Thumbnail: Custom or default
   - Filename: Custom pattern
   - Metadata: Enable/Disable
   - Download Mode: Telegram/URL
   - Upload Mode: Telegram/GoFile

3. **Video Tools (7 Options)**
   - Video Merge: video+video, video+audio, video+subs
   - Video Encoding: Multiple presets (1080p, 720p, 480p, 360p, HEVC, custom)
   - Convert: Document ↔ Video
   - Watermark: Add logo/watermark
   - Trim: Cut specific portions
   - Sample: Generate preview clips
   - MediaInfo: Extract detailed info

4. **Task Management**
   - One task per user limit
   - Multi-user concurrent processing
   - `/s` command to show all running tasks
   - Progress tracking

## Technology Stack
- **Framework**: Pyrogram 2.0.106 (Telegram MTProto)
- **Database**: MongoDB with Motor (async driver)
- **Video Processing**: FFmpeg
- **File Operations**: aiofiles, aiohttp
- **Image Processing**: Pillow

## User Preferences
- Bot designed for Hindi/Hinglish speaking users
- All requirements extracted from reference repositories
- Focus on professional video processing capabilities
- Group-based authorization for controlled access

## Environment Variables Required
```
BOT_TOKEN=           # From @BotFather
API_ID=              # From my.telegram.org
API_HASH=            # From my.telegram.org
OWNER_ID=            # Bot owner's Telegram user ID
SUDO_USERS=          # Comma-separated admin IDs
AUTHORIZED_GROUPS=   # Comma-separated group IDs
MONGO_URI=           # MongoDB connection string
DATABASE_NAME=       # Database name
GOFILE_API_KEY=      # Optional: GoFile upload
LOG_CHANNEL=         # Optional: Log channel ID
```

## Important Implementation Notes
1. **Hold/Active Mode**: Users must send /start in authorized groups to activate bot
2. **Private Chat**: Shows menus but blocks task execution (except for admins)
3. **Merge Validation**: Bot validates file types based on selected merge mode
4. **Encoding Settings**: Users can select presets or configure custom parameters
5. **Task Limits**: One active task per user, but multiple users can process concurrently

## Setup Requirements
1. Python 3.8+
2. MongoDB (local or Atlas)
3. FFmpeg installed
4. Telegram Bot Token and API credentials
5. Environment variables configured

## Commands
### User Commands
- `/start` - Activate/deactivate bot (groups) or show menu (private)
- `/stop` - Stop bot and cancel tasks
- `/s` - Show all running tasks (groups only)
- `/help` - Show help information

### Admin Commands (Owner Only)
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/stats` - View bot statistics
- `/broadcast` - Broadcast message to all users (reply to message)

## Database Schema
### Users Collection
```python
{
    "user_id": int,
    "username": str,
    "settings": {
        "send_as": "document|video",
        "thumbnail": str|None,
        "filename": str,
        "metadata": bool,
        "download_mode": "telegram|url",
        "upload_mode": "telegram|gofile"
    },
    "active_in_group_<id>": bool,
    "is_banned": bool,
    "video_tool_selected": str|None,
    "encoding_settings": dict|None,
    "merge_type": str|None,
    "temp_files": list,
    "created_at": datetime,
    "last_used": datetime
}
```

### Tasks Collection
```python
{
    "user_id": int,
    "task_type": str,
    "status": "processing|completed|cancelled",
    "started_at": datetime,
    "completed_at": datetime|None,
    "progress": int
}
```

## Next Steps / Future Enhancements
- Add batch processing for multiple videos
- Implement task scheduling and queuing
- Add video preview generation
- Create advanced watermark positioning
- Implement detailed progress tracking with ETA
- Add more encoding presets
- Support for additional video formats

## Troubleshooting
- **MongoDB Connection**: Ensure MongoDB is running and MONGO_URI is correct
- **FFmpeg Errors**: Verify FFmpeg is installed: `ffmpeg -version`
- **Bot Not Responding**: Check BOT_TOKEN and API credentials
- **Group Authorization**: Verify group IDs are negative numbers in AUTHORIZED_GROUPS
- **Import Errors**: LSP import warnings are normal in Replit environment

## References
- Original repositories analyzed for features:
  - toonrips/Anime-Leech (video processing features)
  - SunilSharmaNP/ssmerge (merge functionality)
  - SunilSharmaNP/ve (encoding features)

## Deployment Notes
- For Replit: Use MongoDB Atlas (free tier)
- For VPS: Install MongoDB locally
- Use process manager (PM2/systemd) for production
- Regular cleanup of downloads/ directory recommended
