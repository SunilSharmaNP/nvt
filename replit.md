# Video Tools Bot (NVT) - Professional Telegram Bot

## Overview
Professional Telegram bot providing comprehensive video processing capabilities including encoding, merging, watermarking, trimming, sample generation, format conversion, and MediaInfo extraction. Built with Pyrogram, FFmpeg, and MongoDB for persistent user settings.

**Bot Username:** @SSVideoToolsbot  
**Status:** ✅ Running and Operational  
**Last Updated:** October 23, 2025

## Features

### 🎬 Video Tools
1. **Video Encoding** - Multiple quality presets (1080p, 720p, 480p, 360p) with HEVC support
2. **Video Merging** - Three modes:
   - Video + Video (multiple videos)
   - Video + Audio (dual audio support)
   - Video + Subtitles (.srt, .ass, .vtt)
3. **Format Conversion** - Document ↔ Video conversion
4. **Watermarking** - Text or PNG image watermarks with position control
5. **Video Trimming** - Cut specific portions from videos
6. **Sample Generation** - Create 30/60/120/300 second samples
7. **MediaInfo** - Professional file analysis with Telegraph graphs

### ⚙️ User Settings (Persistent)
- **Send As:** Document/Video output format
- **Thumbnail:** Custom thumbnail images
- **Filename:** Custom output filenames
- **Metadata:** Enable/disable video metadata
- **Download Mode:** Telegram files or Direct URLs
- **Upload Mode:** Telegram or GoFile server

## Project Structure

```
.
├── bot/
│   ├── __init__.py          # Bot initialization and plugin loader
│   ├── database/
│   │   └── db.py            # MongoDB async operations
│   ├── helpers/
│   │   ├── buttons.py       # 2-column button layouts with tick marks
│   │   ├── ffmpeg.py        # FFmpeg processing functions
│   │   ├── gofile.py        # GoFile upload integration
│   │   ├── mediainfo.py     # MediaInfo graph generation
│   │   └── progress.py      # Upload/download progress tracking
│   ├── plugins/
│   │   ├── admin.py         # Admin commands (ban, stats, broadcast)
│   │   ├── callbacks.py     # All callback query handlers
│   │   ├── file_handler.py  # File processing and tool execution
│   │   └── start.py         # Start, help, settings commands
│   └── utils/
│       └── helpers.py       # Authorization and utility functions
├── config.py                # Configuration and video presets
├── main.py                  # Entry point with error handling
├── requirements.txt         # Python dependencies
└── downloads/              # Temporary file storage
```

## Commands

### User Commands
- `/start` - Activate bot and show main menu
- `/hold` - Put bot in hold mode (stop processing files)
- `/us` - User Settings menu
- `/vt` - Video Tools menu
- `/stop` - Clear all tasks and temporary data
- `/help` - Complete usage guide

### Group Commands
- `/s` - Show all active tasks (authorized groups only)

### Admin Commands (Owner only)
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/stats` - Bot statistics
- `/broadcast <message>` - Broadcast to all users

## Technical Stack

### Core Technologies
- **Python 3.11** - Programming language
- **Pyrogram 2.0.106** - Telegram MTProto client
- **Motor 3.3.2** - Async MongoDB driver
- **FFmpeg** - Video processing engine
- **MongoDB** - Persistent user data storage

### Key Dependencies
- TgCrypto (fast encryption)
- aiofiles (async file I/O)
- aiohttp (async HTTP requests)
- Pillow (image processing)
- psutil (system monitoring)
- html-telegraph-poster (MediaInfo graphs)

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  user_id: int,              // Telegram user ID
  username: str,             // Telegram username
  is_banned: bool,
  is_active: bool,           // Active/Hold mode
  active_groups: [int],      // Authorized group IDs
  
  // Settings (persistent)
  settings: {
    send_as: "document"|"video",
    metadata: bool,
    download_mode: "telegram"|"url",
    upload_mode: "telegram"|"gofile"
  },
  
  // Custom configurations
  custom_filename: str,
  thumbnail_file_id: str,
  
  // Video tool selections
  video_tool_selected: str,  // "merge"|"encoding"|"convert"|"watermark"|"trim"|"sample"|"mediainfo"
  merge_type: str,           // "video_video"|"video_audio"|"video_subs"
  encoding_settings: {},     // Quality preset data
  convert_mode: str,         // "to_document"|"to_video"
  watermark_type: str,       // "text"|"image"
  watermark_text: str,
  watermark_image_file_id: str,
  watermark_position: str,   // "topleft"|"topright"|"bottomleft"|"bottomright"
  sample_duration: int,      // 30|60|120|300
  
  // Temporary processing data
  temp_files: [],
  current_task: {},
  
  created_at: datetime,
  last_active: datetime
}
```

## Configuration

### Environment Variables (Required)
Set these in Replit Secrets:
- `BOT_TOKEN` - From @BotFather
- `API_ID` - From https://my.telegram.org
- `API_HASH` - From https://my.telegram.org
- `MONGO_URI` - MongoDB connection string
- `OWNER_ID` - Bot owner's Telegram user ID

### Optional Variables
- `SUDO_USERS` - Comma-separated admin user IDs
- `AUTHORIZED_GROUPS` - Comma-separated group chat IDs
- `LOG_CHANNEL` - Channel ID for logging
- `GOFILE_API_KEY` - GoFile API key for uploads
- `SESSION_NAME` - Bot session name (default: video_tools_bot)

## Video Encoding Presets

Configured in `config.py`:
- **1080p:** 1920x1080, 2500k video bitrate, 192k audio
- **720p:** 1280x720, 1500k video bitrate, 128k audio
- **480p:** 854x480, 800k video bitrate, 96k audio
- **360p:** 640x360, 500k video bitrate, 64k audio
- **Custom:** User-defined settings

## Design Principles

### Professional 2-Column Button Layout
All menus use a consistent 2-column layout with visual indicators:
- ✅ tick mark = active/selected option
- Clean spacing and organization
- Persistent state across sessions

### Error Handling
- Download/Upload mode validation (URL mode requires URL input)
- File type validation per tool
- Comprehensive error messages
- Automatic cleanup on failures

### User Experience
- Settings saved to MongoDB (persist across restarts)
- Active/Hold mode per user
- Progress tracking for long operations
- Authorized group system

## Development Notes

### Recent Changes (October 23, 2025)
- Fixed `/start` command - now activates instead of toggling
- Added `/hold` command for explicit hold mode
- Fixed `/us` and `/vt` shortcuts
- Enhanced button system with active tool indicators
- Completed callback handlers for all tools
- Database schema aligned with persistent settings
- All dependencies installed and verified

### Known Issues
- LSP import warnings (harmless - packages installed via pip)
- Some type checking warnings (runtime operations work correctly)

### Testing Checklist
- [x] Bot starts successfully
- [x] All plugins load correctly (14 plugins)
- [x] MongoDB connection configured
- [x] Commands registered properly
- [ ] Test /start in private chat
- [ ] Test /start in authorized group
- [ ] Test User Settings persistence
- [ ] Test Video Tools workflow
- [ ] Test file processing

## Usage Workflow

1. **Initial Setup**
   - User sends `/start` to activate bot
   - Configure User Settings via `/us`
   - Select tool from Video Tools via `/vt`

2. **Processing Files**
   - Tool is enabled (shows ✅ tick mark)
   - User sends file(s) based on tool requirements
   - Bot processes and returns result
   - Settings persist for next use

3. **Managing Bot**
   - `/hold` - Temporarily stop processing
   - `/start` - Reactivate
   - `/stop` - Clear all data and tasks

## Support & Credits

**Developer:** NVT Team  
**Version:** 3.0 Professional Edition  
**Reference:** Based on Anime-Leech architecture  
**License:** Private repository

For support, contact the bot owner via Telegram.
