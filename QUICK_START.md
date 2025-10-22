# ⚡ Quick Start Guide

## For Replit Users

### 1. Configure Environment Variables

Click on the "Secrets" tool (🔒 icon) in the left sidebar and add these secrets:

**Required:**
- `BOT_TOKEN` - Get from @BotFather on Telegram
- `API_ID` - Get from https://my.telegram.org
- `API_HASH` - Get from https://my.telegram.org
- `OWNER_ID` - Your Telegram user ID (get from @userinfobot)
- `AUTHORIZED_GROUPS` - Comma-separated group IDs (e.g., `-1001234567890,-1009876543210`)
- `MONGO_URI` - MongoDB connection string

**Optional:**
- `SUDO_USERS` - Comma-separated admin user IDs
- `GOFILE_API_KEY` - For GoFile uploads
- `LOG_CHANNEL` - Channel ID for logs

### 2. Setup MongoDB

**Option A: MongoDB Atlas (Recommended for Replit)**
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create free account and cluster
3. Get connection string
4. Add as `MONGO_URI` secret

**Option B: Use provided MongoDB**
- Set `MONGO_URI` to `mongodb://localhost:27017`

### 3. Run the Bot

Click the "Run" button at the top!

The bot will automatically start and you'll see:
```
✅ Bot Started as @your_bot_username
```

### 4. Test Your Bot

1. Open Telegram and find your bot
2. Send `/start` command
3. You should see the welcome menu!

## For Local Development

### 1. Clone and Install
```bash
git clone <repo-url>
cd video-tools-bot
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
python setup.py
```

### 3. Start Bot
```bash
python main.py
```

## How to Use

### In Private Chat (Owner Only)
1. Send `/start` to see main menu
2. Configure "User Settings"
3. Select tool from "Video Tools"
4. Send files to process

### In Authorized Groups
1. Add bot to group
2. Send `/start` to activate
3. Configure settings
4. Select tool and send files
5. Use `/s` to see active tasks
6. Use `/stop` to deactivate bot for yourself

## Commands

- `/start` - Activate bot / Show menu
- `/stop` - Stop bot and cancel tasks
- `/s` - Show running tasks (groups)
- `/help` - Show help information

## Admin Only
- `/ban <user_id>` - Ban user
- `/unban <user_id>` - Unban user
- `/stats` - Bot statistics
- `/broadcast` - Send message to all users

## Need Help?

Check **SETUP_GUIDE.md** for detailed setup instructions!
