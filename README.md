# 🎬 Professional Video Tools Bot

A powerful Telegram bot for advanced video processing with multiple tools including encoding, merging, conversion, watermarking, trimming, and more.

## ✨ Features

### 🎥 Video Tools
- **Video Encoding** - Multiple quality presets (1080p, 720p, 480p, 360p) with HEVC support
- **Video Merging** - Merge videos, add audio tracks, or embed subtitles
- **Format Conversion** - Convert between document and video formats
- **Watermarking** - Add custom watermarks to videos
- **Video Trimming** - Cut specific portions from videos
- **Sample Generation** - Create preview clips
- **MediaInfo** - Extract detailed video information

### ⚙️ User Settings
- Send as Document or Video
- Custom Thumbnails
- Filename Customization
- Metadata Control
- Download Mode (Telegram/URL)
- Upload Mode (Telegram/GoFile)

### 🔒 Authorization System
- Authorized group-only operation
- Hold/Active mode toggle
- Admin override for private chats
- User ban/unban system

### 📊 Task Management
- One task per user limit
- Multi-user concurrent processing
- Task status tracking with `/s` command
- Progress monitoring

## 🚀 Setup

### Prerequisites
- Python 3.8+
- MongoDB
- FFmpeg

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd video-tools-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your values
```

5. Configure MongoDB:
- Install MongoDB locally or use MongoDB Atlas
- Update MONGO_URI in .env

6. Run the bot:
```bash
python main.py
```

## 🔧 Configuration

Edit `.env` file with your configuration:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Bot Owner/Admin Configuration
OWNER_ID=your_telegram_user_id_here
SUDO_USERS=user_id_1,user_id_2

# Authorized Groups (comma-separated group IDs)
AUTHORIZED_GROUPS=-1001234567890

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=video_tools_bot
```

## 📝 Usage

### For Users

1. **In Private Chat:**
   - Use `/start` to see main menu
   - Configure user settings
   - Note: Task execution restricted (join authorized group)

2. **In Authorized Groups:**
   - Use `/start` to activate bot (toggle hold/active mode)
   - Configure settings via User Settings menu
   - Select tool from Video Tools menu
   - Send required files
   - Bot processes and returns result

3. **Commands:**
   - `/start` - Activate bot / Show main menu
   - `/stop` - Stop bot and cancel tasks
   - `/s` - Show all running tasks
   - `/help` - Show help information

### For Admins

Additional commands for bot owner:
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/stats` - View bot statistics
- `/broadcast` - Broadcast message to all users (reply to message)

## 🎯 Workflow

1. **User Settings Configuration:**
   - Set output format preference
   - Configure thumbnail (optional)
   - Set custom filename (optional)
   - Enable/disable metadata
   - Choose download/upload modes

2. **Tool Selection:**
   - Choose from 7 available tools
   - Configure tool-specific settings
   - For encoding: select quality preset
   - For merging: select merge type

3. **File Processing:**
   - Send required file(s)
   - Bot validates and processes
   - Progress updates shown
   - Receive processed file

## 🏗️ Architecture

```
video-tools-bot/
├── bot/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── buttons.py
│   │   ├── ffmpeg_helper.py
│   │   ├── download_helper.py
│   │   └── upload_helper.py
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── callbacks.py
│   │   ├── file_handler.py
│   │   └── admin.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── downloads/
├── config.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Technology Stack

- **Pyrogram** - Telegram MTProto API framework
- **FFmpeg** - Video processing
- **MongoDB** - Database
- **Motor** - Async MongoDB driver
- **aiofiles** - Async file operations
- **aiohttp** - Async HTTP requests

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For issues, feature requests, or support:
- Open an issue on GitHub
- Contact bot owner via Telegram

## ⚠️ Important Notes

- Bot works only in authorized groups
- One task per user at a time
- Large files may take time to process
- GoFile upload requires API key
- Private chat limited to viewing menus only (except for admins)

## 🔄 Updates

Regular updates include:
- New video processing features
- Performance improvements
- Bug fixes
- Enhanced user experience

---

Made with ❤️ for professional video processing on Telegram
