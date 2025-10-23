from pyrogram import Client
from config import Config

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=Config.SESSION_NAME,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="bot/plugins")
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f"✅ Bot Started as @{me.username}")

    async def stop(self):
        await super().stop()
        print("🛑 Bot Stopped")
        
