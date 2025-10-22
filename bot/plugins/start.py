from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.helpers.buttons import main_menu_buttons
from bot.utils.helpers import is_admin, is_authorized_group
from config import Config

WELCOME_TEXT = """
👋 **Welcome to Video Tools Bot!**

🎬 **Professional Video Processing at Your Fingertips**

This bot provides powerful video editing tools including:
• Video Encoding (Multiple Quality Presets)
• Video Merging (Video+Video, Video+Audio, Video+Subs)
• Format Conversion (Document↔Video)
• Watermarking
• Video Trimming
• Sample Generation
• MediaInfo Extraction

⚙️ **Getting Started:**
1. First, configure your **User Settings** for customized output
2. Select a tool from **Video Tools** menu
3. Send your video file(s) to start processing

📋 **Important Notes:**
• Set your preferences before starting tasks
• One task per user at a time
• Bot works in authorized groups only
• Private chat limited (use in authorized groups)

Choose an option below to continue:
"""

@Client.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    """Handle /start command in private chat"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Add user to database
    await db.add_user(user_id, username)
    
    # Check if user is banned
    if await db.is_user_banned(user_id):
        await message.reply_text("❌ You are banned from using this bot.")
        return
    
    # Send welcome message with main menu
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
    
    # Add user to database
    await db.add_user(user_id, username)
    
    # Check if user is banned
    if await db.is_user_banned(user_id):
        await message.reply_text("❌ You are banned from using this bot.")
        return
    
    # Check if group is authorized
    if not await is_authorized_group(chat_id):
        await message.reply_text(
            "⚠️ **Unauthorized Group**\n\n"
            "This bot works only in authorized groups.\n"
            f"Please contact the owner to authorize this group.\n\n"
            f"Owner: {Config.OWNER_ID}"
        )
        return
    
    # Toggle user active status in this group
    is_active = await db.is_user_active(user_id, chat_id)
    await db.set_user_active(user_id, chat_id, not is_active)
    
    if not is_active:
        # User is now active
        await message.reply_text(
            f"✅ **Bot Activated for {message.from_user.mention}**\n\n"
            "🎬 You can now use all video tools!\n\n"
            "⚙️ **Quick Setup:**\n"
            "1. Configure your User Settings first\n"
            "2. Choose a video tool from Video Tools menu\n"
            "3. Send your files to start processing\n\n"
            "Use the buttons below to get started:",
            reply_markup=main_menu_buttons()
        )
    else:
        # User is now in hold mode
        await message.reply_text(
            f"⏸ **Bot Deactivated for {message.from_user.mention}**\n\n"
            "The bot is now in hold mode for you.\n"
            "Use /start again to activate when you need it."
        )

@Client.on_message(filters.command("stop"))
async def stop_command(client: Client, message: Message):
    """Handle /stop command"""
    user_id = message.from_user.id
    
    # Cancel any active tasks
    await db.cancel_task(user_id)
    
    # Clear temporary files
    await db.clear_temp_files(user_id)
    
    # If in group, set to hold mode
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
            "All your active tasks have been cancelled and temporary files cleared."
        )

@Client.on_message(filters.command("s") & filters.group)
async def show_tasks(client: Client, message: Message):
    """Show all running tasks in the group"""
    chat_id = message.chat.id
    
    # Check if group is authorized
    if not await is_authorized_group(chat_id):
        return
    
    # Get all active tasks
    tasks = await db.get_all_active_tasks()
    
    if not tasks:
        await message.reply_text("📊 **No Active Tasks**\n\nNo video processing tasks are currently running.")
        return
    
    # Build task list message
    text = "📊 **Active Tasks**\n\n"
    for i, task in enumerate(tasks, 1):
        user = await client.get_users(task["user_id"])
        task_type = task.get("task_type", "Unknown")
        progress = task.get("progress", 0)
        
        text += f"{i}. **{user.mention}**\n"
        text += f"   • Task: {task_type}\n"
        text += f"   • Progress: {progress}%\n\n"
    
    await message.reply_text(text)

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    help_text = """
📚 **Video Tools Bot - Help Guide**

**Available Commands:**
• `/start` - Activate/Deactivate bot (in groups) or show main menu (in private)
• `/stop` - Stop bot and cancel all tasks
• `/s` - Show all running tasks (groups only)
• `/help` - Show this help message

**How to Use:**

**1️⃣ User Settings**
Configure your preferences before processing:
• **Send as**: Document or Video
• **Thumbnail**: Set custom thumbnail for uploads
• **Filename**: Customize output filename
• **Metadata**: Enable/Disable metadata
• **Download Mode**: Telegram or Direct URL
• **Upload Mode**: Telegram or GoFile server

**2️⃣ Video Tools**
Choose from 7 powerful tools:

🔗 **Video Merge**
   • Video + Video: Merge multiple videos
   • Video + Audio: Replace/add audio track
   • Video + Subtitles: Add subtitle file

🎞️ **Video Encoding**
   • Multiple quality presets (1080p, 720p, 480p, 360p)
   • HEVC encoding for smaller file sizes
   • Custom encoding settings (CRF, bitrate, codec, etc.)

🔄 **Convert**
   • Document to Video
   • Video to Document

©️ **Watermark**
   • Add image watermark to videos

✂️ **Trim Video**
   • Cut specific portions from video

🎬 **Sample Video**
   • Generate sample clips

📊 **MediaInfo**
   • Get detailed video information

**3️⃣ Processing Flow**
1. Configure User Settings
2. Select Video Tool
3. Send required file(s)
4. Wait for processing
5. Receive processed file

**Important Notes:**
• Only one task per user at a time
• Bot works in authorized groups only
• Private chat has limited functionality (unless you're an admin)
• Always set User Settings before starting tasks

Need more help? Contact bot owner: {Config.OWNER_ID}
"""
    await message.reply_text(help_text)
