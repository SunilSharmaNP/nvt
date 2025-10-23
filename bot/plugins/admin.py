from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.utils.helpers import is_admin
from config import Config

@Client.on_message(filters.command("ban") & filters.user(Config.OWNER_ID))
async def ban_user(client: Client, message: Message):
    """Ban a user from using the bot"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /ban <user_id>")
        return

    try:
        target_user_id = int(message.command[1])
        await db.ban_user(target_user_id)
        await message.reply_text(f"✅ User {target_user_id} को ban कर दिया गया है।")
    except ValueError:
        await message.reply_text("❌ Invalid user ID")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("unban") & filters.user(Config.OWNER_ID))
async def unban_user(client: Client, message: Message):
    """Unban a user"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /unban <user_id>")
        return

    try:
        target_user_id = int(message.command[1])
        await db.unban_user(target_user_id)
        await message.reply_text(f"✅ User {target_user_id} को unban कर दिया गया है।")
    except ValueError:
        await message.reply_text("❌ Invalid user ID")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("broadcast") & filters.user(Config.OWNER_ID))
async def broadcast(client: Client, message: Message):
    """Broadcast message to all users"""
    if not message.reply_to_message:
        await message.reply_text("❌ एक message को reply करें broadcast करने के लिए")
        return

    users = []
    cursor = db.users.find({})
    async for user in cursor:
        users.append(user["user_id"])

    success = 0
    failed = 0

    status_msg = await message.reply_text(f"📢 {len(users)} users को broadcast कर रहे हैं...")

    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            success += 1
        except:
            failed += 1

    await status_msg.edit_text(
        f"📢 **Broadcast Complete**\n\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
    )

@Client.on_message(filters.command("stats") & filters.user(Config.OWNER_ID))
async def stats(client: Client, message: Message):
    """Show bot statistics"""
    total_users = await db.users.count_documents({})
    banned_users = await db.users.count_documents({"is_banned": True})
    active_tasks = await db.tasks.count_documents({"status": "processing"})

    stats_text = f"""
📊 **Bot Statistics**

👥 **Users:**
• Total: {total_users}
• Banned: {banned_users}
• Active: {total_users - banned_users}

⚙️ **Tasks:**
• Currently Running: {active_tasks}

🔧 **System:**
• Authorized Groups: {len(Config.AUTHORIZED_GROUPS)}
• Sudo Users: {len(Config.SUDO_USERS)}
"""

    await message.reply_text(stats_text)
