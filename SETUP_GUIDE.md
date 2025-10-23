# 🚀 Video Tools Bot - Complete Setup Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- MongoDB (local or Atlas)
- FFmpeg installed
- Telegram Bot Token
- Telegram API credentials

## Step 1: Get Telegram Credentials

### 1.1 Create a Bot
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the **BOT_TOKEN** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 1.2 Get API Credentials
1. Visit https://my.telegram.org
2. Login with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Save your **API_ID** and **API_HASH**

### 1.3 Get Your User ID
1. Open Telegram and search for **@userinfobot**
2. Send `/start` to the bot
3. It will reply with your **User ID**
4. This will be your **OWNER_ID**

### 1.4 Get Group IDs (for authorized groups)
1. Add **@userinfobot** to your group
2. It will show the group ID (negative number like: `-1001234567890`)
3. Remove the bot after getting the ID

## Step 2: Setup MongoDB

### Option A: Local MongoDB
```bash
# Install MongoDB on Ubuntu/Debian
sudo apt update
sudo apt install mongodb

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Your MONGO_URI will be: mongodb://localhost:27017
```

### Option B: MongoDB Atlas (Free Cloud Database)
1. Visit https://www.mongodb.com/cloud/atlas/register
2. Create a free account
3. Create a new cluster (free tier)
4. Create a database user
5. Whitelist your IP (or use 0.0.0.0/0 for all IPs)
6. Get your connection string (MONGO_URI)
   - Format: `mongodb+srv://username:password@cluster.mongodb.net/`

## Step 3: Install FFmpeg

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS:
```bash
brew install ffmpeg
```

### Verify Installation:
```bash
ffmpeg -version
```

## Step 4: Install Bot Dependencies

```bash
# Clone or download the bot repository
cd video-tools-bot

# Install Python dependencies
pip install -r requirements.txt
```

## Step 5: Configure the Bot

### Method 1: Automated Setup (Recommended)
```bash
python setup.py
```
Follow the interactive prompts to configure your bot.

### Method 2: Manual Setup
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your values:
```env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
OWNER_ID=your_telegram_user_id_here
SUDO_USERS=user_id_1,user_id_2
AUTHORIZED_GROUPS=-1001234567890,-1009876543210
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=video_tools_bot
```

## Step 6: Run the Bot

```bash
python main.py
```

You should see:
```
✅ Bot Started as @your_bot_username
```

## Step 7: Test the Bot

1. **In Private Chat:**
   - Open your bot in Telegram
   - Send `/start`
   - You should see the welcome menu
   - As owner, you can use all features in private chat

2. **In Authorized Group:**
   - Add the bot to one of your authorized groups
   - Send `/start` to activate the bot
   - You should see the activation message with buttons

## Configuration Options

### User Settings
- **Send as**: Document or Video format
- **Thumbnail**: Custom thumbnail for videos
- **Filename**: Custom filename pattern
- **Metadata**: Enable/disable file metadata
- **Download Mode**: Telegram or URL (for direct download links)
- **Upload Mode**: Telegram or GoFile server

### Video Tools
1. **Video Merge**
   - Video + Video: Merge multiple videos
   - Video + Audio: Replace audio track
   - Video + Subtitles: Add subtitle file

2. **Video Encoding**
   - Quality presets: 1080p, 720p, 480p, 360p
   - HEVC variants for smaller file sizes
   - Custom encoding parameters

3. **Convert**: Document ↔ Video conversion

4. **Watermark**: Add logo/watermark to videos

5. **Trim**: Cut specific portions from video

6. **Sample**: Generate preview clips

7. **MediaInfo**: Extract detailed video information

## Admin Commands

Only bot owner can use:
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/stats` - View bot statistics
- `/broadcast` - Broadcast message (reply to a message)

## Troubleshooting

### Bot doesn't respond
- Check if bot is running: `python main.py`
- Verify BOT_TOKEN is correct
- Check bot logs for errors

### MongoDB connection error
- Verify MongoDB is running: `sudo systemctl status mongodb`
- Check MONGO_URI in .env file
- For Atlas, verify IP whitelist and credentials

### FFmpeg not found
- Install FFmpeg: `sudo apt install ffmpeg`
- Verify: `ffmpeg -version`

### Bot works in private but not in groups
- Check AUTHORIZED_GROUPS in .env
- Make sure group ID is correct (negative number)
- Send /start in the group to activate

### Permission errors
- Make sure downloads/ directory exists and is writable
- Check file permissions: `chmod +x main.py`

## Security Best Practices

1. **Never share your .env file** - it contains sensitive credentials
2. **Keep BOT_TOKEN private** - anyone with it can control your bot
3. **Limit authorized groups** - only add groups you trust
4. **Regular updates** - keep dependencies updated
5. **Monitor logs** - check for unusual activity

## Performance Tips

1. **Adjust FFMPEG_THREADS** based on your CPU cores
2. **Set MAX_FILE_SIZE** according to your storage
3. **Use GoFile** for large file uploads to save Telegram bandwidth
4. **Clean downloads folder** regularly

## Deployment Options

### Local Server/VPS
```bash
# Use screen or tmux to keep bot running
screen -S videobot
python main.py
# Press Ctrl+A, then D to detach
```

### Docker (if supported)
```bash
docker build -t video-tools-bot .
docker run -d --name videobot video-tools-bot
```

### Process Manager (PM2)
```bash
npm install -g pm2
pm2 start main.py --name video-tools-bot --interpreter python3
pm2 save
pm2 startup
```

## Support

For issues or questions:
1. Check this guide first
2. Review bot logs for errors
3. Verify all configurations
4. Contact bot maintainer

---

Made with ❤️ for professional video processing
