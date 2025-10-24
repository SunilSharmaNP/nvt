from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.helpers.buttons import main_menu_buttons
from bot.utils.helpers import is_admin, is_authorized_group
from config import Config

WELCOME_TEXT = """
👋 **Welcome to Professional Video Tools Bot!**

🎬 **Advanced Video Processing Platform**

This bot provides powerful video editing tools:
• Video Encoding (Multiple Quality Presets)
• Video Merging (Video+Video, Video+Audio, Video+Subs)
• Format Conversion (Document↔Video)
• Watermarking
• Video Trimming
• Sample Generation
• MediaInfo Extraction

⚙️ **Getting Started:**
1. Configure your **User Settings** first
2. Select a tool from **Video Tools** menu
3. Send your video file

📋 **Important Notes:**
• One task at a time per user
• Works in authorized groups only
• Configure settings before processing

Choose an option below to get started:
"""

@Client.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    """Handle /start command in private chat"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    await db.add_user(user_id, username)
    
    if await db.is_user_banned(user_id):
        await message.reply_text("❌ You are banned from using this bot.")
        return
    
    await message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu_buttons()
    )

@Client.on_message(filters.command("start") & filters.group)
async def start_group(client: Client, message: Message):
    """Handle /start command in group"""
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    
    await db.add_user(user_id, username)
    
    if await db.is_user_banned(user_id):
        await message.reply_text("❌ You are banned from using this bot.")
        return
    
    if not await is_authorized_group(chat_id):
        await message.reply_text(
            "⚠️ **Unauthorized Group**\n\n"
            "This bot only works in authorized groups.\n"
            f"Please contact the owner.\n\n"
            f"Owner ID: `{Config.OWNER_ID}`"
        )
        return
    
    is_active = await db.is_user_active(user_id, chat_id)
    await db.set_user_active(user_id, chat_id, not is_active)
    
    if not is_active:
        await message.reply_text(
            f"✅ **Bot Activated for {message.from_user.mention}**\n\n"
            "🎬 You can now use all video tools!\n\n"
            "⚙️ **Quick Setup:**\n"
            "1. Configure User Settings first\n"
            "2. Select a tool from Video Tools menu\n"
            "3. Send your files\n\n"
            "Use the buttons below to get started:",
            reply_markup=main_menu_buttons()
        )
    else:
        await message.reply_text(
            f"⏸ **Bot Deactivated for {message.from_user.mention}**\n\n"
            "Bot is now in hold mode.\n"
            "Use /start again to activate."
        )

@Client.on_message(filters.command("stop"))
async def stop_command(client: Client, message: Message):
    """Handle /stop command"""
    user_id = message.from_user.id
    
    await db.cancel_task(user_id)
    await db.clear_temp_files(user_id)
    
    if message.chat.type != "private":
        await db.set_user_active(user_id, message.chat.id, False)
        await message.reply_text(
            "🛑 **Bot Stopped**\n\n"
            "• Active tasks cancelled\n"
            "• Temporary files cleared\n"
            "• Bot set to hold mode\n\n"
            "Use /start to activate again."
        )
    else:
        await message.reply_text(
            "🛑 **Tasks Cancelled**\n\n"
            "All active tasks have been cancelled."
        )

@Client.on_message(filters.command("s") & filters.group)
async def show_tasks(client: Client, message: Message):
    """Show all running tasks in the group"""
    chat_id = message.chat.id
    
    if not await is_authorized_group(chat_id):
        return
    
    tasks = await db.get_all_active_tasks()
    
    if not tasks:
        await message.reply_text("📊 **No Active Tasks**\n\nNo video processing tasks are currently running.")
        return
    
    text = "📊 **Active Tasks**\n\n"
    for i, task in enumerate(tasks, 1):
        try:
            user = await client.get_users(task["user_id"])
            task_type = task.get("task_type", "Unknown")
            progress = task.get("progress", 0)
            
            text += f"{i}. **{user.mention}**\n"
            text += f"   • Task: {task_type}\n"
            text += f"   • Progress: {progress}%\n\n"
        except:
            continue
    
    await message.reply_text(text)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    help_text = f"""
📚 **Video Tools Bot - Help Guide**

**Available Commands:**
• `/start` - Activate/deactivate bot
• `/stop` - Stop bot and cancel tasks
• `/s` - Show all running tasks (groups only)
• `/help` - Show this help message

**How to Use:**

**1️⃣ User Settings**
Configure your preferences before processing:
• **Send as**: Document or Video
• **Thumbnail**: Set custom thumbnail
• **Filename**: Customize output filename
• **Metadata**: Enable/Disable metadata
• **Download Mode**: Telegram or Direct URL
• **Upload Mode**: Telegram or GoFile server

**2️⃣ Video Tools**
Choose from 7 powerful tools:

🎞️ **Video Encoding**
   • Multiple quality presets (1080p, 720p, 480p, 360p)
   • HEVC encoding for smaller files
   • Custom encoding settings

🔗 **Video Merge**
   • Video + Video: Merge multiple videos
   • Video + Audio: Replace/add audio track
   • Video + Subtitles: Add subtitle file

✂️ **Trim Video**
   • Cut specific portions from video

🎬 **Sample Video**
   • Generate sample clips

©️ **Watermark**
   • Add image watermarks to videos

📊 **MediaInfo**
   • Get detailed video information

🔄 **Convert**
   • Document to Video or Video to Document

**Important Notes:**
• One task per user at a time
• Works in authorized groups only
• Configure User Settings first

Need more help? Contact owner: `{Config.OWNER_ID}`
"""
    await message.reply_text(help_text)
