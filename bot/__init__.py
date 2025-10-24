import os
from pyrogram import Client
from config import Config

class Bot(Client):
    def __init__(self):
        # Create downloads directory
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
        
        super().__init__(
            name=Config.SESSION_NAME,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
            workers=50
        )
    
    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f"\n✅ Bot Started Successfully!")
        print(f"👤 Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"📝 First Name: {me.first_name}")
        print(f"\n🎬 Video Tools Bot is now running...\n")
    
    async def stop(self):
        # Cleanup all active tasks
        from bot.database import db
        try:
            await db.tasks.update_many(
                {"status": "processing"},
                {"$set": {"status": "cancelled"}}
            )
        except:
            pass
        
        await super().stop()
        print("\n🛑 Bot Stopped\n")
