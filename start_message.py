#!/usr/bin/env python3
"""
Display setup instructions for the Video Tools Bot
"""

print("""
╔═══════════════════════════════════════════════════════════════╗
║          🎬 Video Tools Bot - Professional Edition            ║
╚═══════════════════════════════════════════════════════════════╝

📋 SETUP REQUIRED

Before the bot can run, you need to configure it with your credentials.

🔧 Quick Setup Steps:

1️⃣  Run the setup wizard:
   python setup.py

2️⃣  Or manually edit .env file with:
   • BOT_TOKEN (from @BotFather)
   • API_ID & API_HASH (from my.telegram.org)
   • OWNER_ID (your Telegram user ID)
   • AUTHORIZED_GROUPS (group IDs)
   • MONGO_URI (MongoDB connection string)

3️⃣  Then start the bot:
   python main.py

📚 Need help? Check these guides:
   • QUICK_START.md - Fast setup guide
   • SETUP_GUIDE.md - Detailed instructions
   • README.md - Full documentation

🧪 Test your setup:
   python test_setup.py

═══════════════════════════════════════════════════════════════

For Replit users:
1. Add secrets in the Secrets panel (🔒):
   BOT_TOKEN, API_ID, API_HASH, OWNER_ID, AUTHORIZED_GROUPS, MONGO_URI
2. Click the Run button

For MongoDB:
• Free option: MongoDB Atlas (https://mongodb.com/cloud/atlas)
• Or install locally: sudo apt install mongodb

═══════════════════════════════════════════════════════════════
""")
