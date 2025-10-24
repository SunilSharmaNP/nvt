# Professional Telegram Video Tools Bot

A powerful Telegram bot for professional video processing with multiple encoding, merging, and editing features.

## Features

### Video Tools
- **Video Encoding**: Multiple quality presets (1080p, 720p, 480p, 360p) with H.264 and HEVC codecs
- **Video Merging**: 
  - Video + Video (merge multiple videos)
  - Video + Audio (replace/add audio tracks)
  - Video + Subtitles (add subtitle files)
- **Video Trimming**: Cut specific portions from videos
- **Sample Generation**: Create sample clips from videos
- **Watermarking**: Add image watermarks with position control
- **MediaInfo**: Get detailed video information
- **Format Conversion**: Convert between document and video formats

### User Settings
- Send files as Document or Video
- Custom thumbnail support
- Filename customization
- Metadata control
- Download mode (Telegram/URL)
- Upload mode (Telegram/GoFile)

### Admin Features
- User ban/unban system
- Broadcast messages to all users
- Bot statistics
- Authorized groups control

## Bot Commands

### User Commands
- `/start` - Activate/deactivate bot
- `/stop` - Stop bot and cancel tasks
- `/s` - Show running tasks (groups only)
- `/help` - Show help guide
- `/clearthumb` - Clear custom thumbnail
- `/defaultname` - Reset filename to default

### Admin Commands (Owner Only)
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/broadcast` - Broadcast message (reply to message)
- `/stats` - Show bot statistics

## Technology Stack

- **Framework**: Pyrogram 2.0.106
- **Database**: MongoDB (Motor async driver)
- **Video Processing**: FFmpeg
- **Language**: Python 3.11
- **Async**: asyncio with aiofiles, aiohttp

## Project Structure

```
.
├── bot/
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                 # MongoDB database operations
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── buttons.py            # Inline keyboard buttons
│   │   ├── download_helper.py    # Download with progress tracking
│   │   ├── upload_helper.py      # Upload to Telegram/GoFile
│   │   └── ffmpeg_helper.py      # FFmpeg video processing
│   ├── plugins/
│   │   ├── admin.py              # Admin commands
│   │   ├── callbacks.py          # Callback query handlers
│   │   ├── media_handler.py      # Media file processing
│   │   ├── start.py              # Start/stop commands
│   │   └── user_inputs.py        # Text/photo input handlers
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py            # Utility functions
│   └── __init__.py               # Bot client initialization
├── downloads/                     # Temporary downloads directory
├── assets/                        # Menu images (optional)
├── config.py                      # Configuration and presets
├── main.py                        # Bot entry point
└── requirements.txt               # Python dependencies
```

## Configuration

All settings are configured via environment variables (Replit Secrets):

### Required Variables
- `BOT_TOKEN` - Your Telegram bot token from @BotFather
- `API_ID` - Your Telegram API ID from https://my.telegram.org/apps
- `API_HASH` - Your Telegram API Hash
- `OWNER_ID` - Your Telegram user ID
- `MONGO_URI` - MongoDB connection string

### Optional Variables
- `SUDO_USERS` - Comma-separated sudo user IDs
- `AUTHORIZED_GROUPS` - Comma-separated authorized group IDs
- `DOWNLOAD_DIR` - Downloads directory (default: downloads)
- `MAX_FILE_SIZE` - Max file size in bytes (default: 2GB)
- `GOFILE_API_KEY` - GoFile API key for uploads
- `FFMPEG_THREADS` - FFmpeg thread count (default: 2)
- `SESSION_NAME` - Bot session name (default: video_tools_bot)
- `LOG_CHANNEL` - Log channel ID (optional)

## How to Use

### 1. User Settings Configuration
Before processing videos, configure your preferences:
- Go to **User Settings** menu
- Set your preferred output format (Document/Video)
- Upload a custom thumbnail (optional)
- Configure metadata, download, and upload modes

### 2. Video Processing Workflow

#### Encoding
1. Click **Video Tools** → **Video Encoding**
2. Select quality preset (or custom settings)
3. Send your video file
4. Bot will download, encode, and upload

#### Merging Videos
1. Click **Video Tools** → **Video Merge** → **Video + Video**
2. Send first video
3. Send second video
4. Bot will merge and upload

#### Merging Audio
1. Click **Video Tools** → **Video Merge** → **Video + Audio**
2. Send video file
3. Send audio file
4. Bot will merge and upload

#### Adding Subtitles
1. Click **Video Tools** → **Video Merge** → **Video + Subtitles**
2. Send video file
3. Send subtitle file (.srt, .ass, .vtt)
4. Bot will merge and upload

#### Trimming
1. Click **Video Tools** → **Trim Video**
2. Send trim times in format: `start:end` (in seconds)
   - Example: `10:120` (trim from 10s to 120s)
3. Send video file (or vice versa)
4. Bot will trim and upload

#### Adding Watermark
1. Click **Video Tools** → **Add Watermark**
2. Select watermark position
3. Send video file
4. Send watermark image
5. Bot will process and upload

#### Sample Video
1. Click **Video Tools** → **Sample Video**
2. Select duration (30s, 60s, 90s, etc.)
3. Send video file
4. Bot will create sample from middle of video

#### MediaInfo
1. Click **Video Tools** → **MediaInfo**
2. Send video file
3. Bot will show detailed media information

## Database Schema

### Users Collection
```javascript
{
  user_id: Number,
  username: String,
  settings: {
    send_as: String,          // 'document' or 'video'
    thumbnail: String,         // thumbnail file path
    filename: String,          // filename pattern
    metadata: Boolean,         // include metadata
    download_mode: String,     // 'telegram' or 'url'
    upload_mode: String        // 'telegram' or 'gofile'
  },
  is_active: Boolean,
  is_banned: Boolean,
  video_tool_selected: String,
  encoding_settings: Object,
  merge_type: String,
  merge_queue: Array,
  temp_files: Array,
  watermark_position: String,
  trim_settings: Object,
  sample_duration: String,
  active_in_group_<group_id>: Boolean,
  created_at: Date,
  last_used: Date
}
```

### Tasks Collection
```javascript
{
  user_id: Number,
  task_type: String,
  status: String,            // 'processing', 'completed', 'cancelled'
  started_at: Date,
  completed_at: Date,
  progress: Number
}
```

## Video Quality Presets

### H.264 Presets
- **1080p**: 1920x1080, CRF 23, 5000k bitrate, 192k audio
- **720p**: 1280x720, CRF 23, 3000k bitrate, 128k audio
- **480p**: 854x480, CRF 23, 1500k bitrate, 128k audio
- **360p**: 640x360, CRF 23, 800k bitrate, 96k audio

### HEVC (H.265) Presets
- **1080p HEVC**: 1920x1080, CRF 28, 3500k bitrate, 192k audio
- **720p HEVC**: 1280x720, CRF 28, 2000k bitrate, 128k audio
- **480p HEVC**: 854x480, CRF 28, 1000k bitrate, 128k audio

All presets use:
- Codec: libx264 or libx265
- Audio: AAC
- Pixel Format: yuv420p
- Preset: medium

## Important Notes

1. **One Task Per User**: Users can only run one video processing task at a time
2. **Authorized Groups**: Bot only works in configured authorized groups
3. **Group Activation**: Users must activate bot in groups using `/start`
4. **Database Persistence**: All user settings and tool selections are saved to MongoDB
5. **Progress Tracking**: Real-time progress updates for download, upload, and processing
6. **Error Handling**: Comprehensive error handling with user-friendly messages
7. **File Cleanup**: Automatic cleanup of temporary files after processing

## Development

### Adding New Video Tools
1. Add button in `bot/helpers/buttons.py`
2. Add callback handler in `bot/plugins/callbacks.py`
3. Implement processing function in `bot/plugins/media_handler.py`
4. Add FFmpeg function in `bot/helpers/ffmpeg_helper.py` (if needed)

### Database Operations
All database operations are in `bot/database/db.py`:
- User management
- Settings persistence
- Task tracking
- Temporary file storage

## Troubleshooting

### Bot not responding
- Check if bot is activated in group (`/start`)
- Verify group is in `AUTHORIZED_GROUPS`
- Check bot logs in console

### Video processing fails
- Ensure FFmpeg is installed
- Check file format is supported
- Verify sufficient disk space
- Check error logs

### Database errors
- Verify `MONGO_URI` is correct
- Check MongoDB connection
- Ensure database is accessible

## License

This is a professional video tools bot for Telegram with full English interface and comprehensive features.

## Support

For support, contact the bot owner via Telegram.
