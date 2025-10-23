from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.helpers.buttons import main_menu_buttons, user_settings_buttons, video_tools_buttons
from bot.utils.helpers import is_admin, is_authorized_group
from config import Config

WELCOME_TEXT = """
👋 **Video Tools Bot में आपका स्वागत है!**

🎬 **Professional Video Processing**

यह bot आपको शक्तिशाली video editing tools प्रदान करता है:
• Video Encoding (Multiple Quality Presets)
• Video Merging (Video+Video, Video+Audio, Video+Subs)
• Format Conversion (Document↔Video)
• Text/Image Watermarking
• Video Trimming
• Sample Generation
• Professional MediaInfo

⚙️ **शुरू करने के लिए:**
1. **User Settings** (/us) से preferences configure करें
2. **Video Tools** (/vt) menu से tool enable करें  
3. अपनी video file भेजें

📋 **Commands:**
• /start - Welcome menu
• /us - User Settings
• /vt - Video Tools
• /hold - Hold mode (stop processing)
• /help - Complete guide

नीचे से option चुनें:
"""

@Client.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    """Handle /start command in private chat"""
    user_id = message.from_user.id
    username = message.from_user.username

    await db.add_user(user_id, username)

    if await db.is_user_banned(user_id):
        await message.reply_text("❌ आप इस bot को उपयोग करने से banned हैं।")
        return

    # Activate user in private mode
    await db.set_user_active(user_id, True)
    
    await message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu_buttons()
    )

@Client.on_message(filters.command("start") & filters.group)
async def start_group(client: Client, message: Message):
    """Handle /start command in group - only activates, doesn't toggle"""
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    await db.add_user(user_id, username)

    if await db.is_user_banned(user_id):
        await message.reply_text("❌ आप इस bot को उपयोग करने से banned हैं।")
        return

    if not await is_authorized_group(chat_id):
        await message.reply_text(
            "⚠️ **Unauthorized Group**\n\n"
            "यह bot केवल authorized groups में काम करता है।\n"
            f"कृपया owner से संपर्क करें।\n\n"
            f"Owner: {Config.OWNER_ID}"
        )
        return

    # Always activate (don't toggle)
    await db.set_user_active(user_id, True, chat_id)
    
    await message.reply_text(
        f"✅ **Bot Activated for {message.from_user.mention}**\n\n"
        "🎬 अब आप सभी video tools का उपयोग कर सकते हैं!\n\n"
        "⚙️ **Quick Setup:**\n"
        "1. /us से User Settings configure करें\n"
        "2. /vt से Video Tools menu खोलें\n"
        "3. Tool enable करके files भेजें\n\n"
        "💡 Hold mode के लिए /hold command use करें।",
        reply_markup=main_menu_buttons()
    )

@Client.on_message(filters.command("hold"))
async def hold_command(client: Client, message: Message):
    """Handle /hold command - put bot in hold mode"""
    user_id = message.from_user.id
    
    await db.cancel_task(user_id)
    await db.clear_temp_files(user_id)
    
    if message.chat.type != "private":
        chat_id = message.chat.id
        await db.set_user_active(user_id, False, chat_id)
        await message.reply_text(
            f"⏸ **Hold Mode Activated for {message.from_user.mention}**\n\n"
            "• All tasks cancelled\n"
            "• Temp files cleared\n"
            "• Bot won't process your files\n\n"
            "Use /start to activate again."
        )
    else:
        await db.set_user_active(user_id, False)
        await message.reply_text(
            "⏸ **Hold Mode Activated**\n\n"
            "Bot won't process your files.\n"
            "Use /start to activate again."
        )

@Client.on_message(filters.command("us"))
async def user_settings_command(client: Client, message: Message):
    """Direct shortcut to User Settings menu"""
    user_id = message.from_user.id
    await db.add_user(user_id, message.from_user.username)
    
    if await db.is_user_banned(user_id):
        await message.reply_text("❌ You are banned.")
        return
    
    user = await db.get_user(user_id)
    settings = user.get("settings", Config.DEFAULT_SETTINGS) if user else Config.DEFAULT_SETTINGS
    
    settings_text = f"""
⚙️ **Your Current Settings**

📄 **Send as:** {settings.get('send_as', 'document').title()}
🖼️ **Thumbnail:** {'Set' if user.get('thumbnail_file_id') else 'Not Set'}
📝 **Filename:** {user.get('custom_filename') or 'Default'}
📋 **Metadata:** {'Enabled' if settings.get('metadata') else 'Disabled'}
⬇️ **Download Mode:** {settings.get('download_mode', 'telegram').upper()}
⬆️ **Upload Mode:** {settings.get('upload_mode', 'telegram').title()}

नीचे से setting बदलें:
"""
    
    await message.reply_text(settings_text, reply_markup=user_settings_buttons())

@Client.on_message(filters.command("vt"))
async def video_tools_command(client: Client, message: Message):
    """Direct shortcut to Video Tools menu"""
    user_id = message.from_user.id
    await db.add_user(user_id, message.from_user.username)
    
    if await db.is_user_banned(user_id):
        await message.reply_text("❌ You are banned.")
        return
    
    user = await db.get_user(user_id)
    active_tool = user.get("video_tool_selected") if user else None
    
    vt_text = "🎬 **Video Tools Menu**\n\n"
    if active_tool:
        vt_text += f"✅ **Active Tool:** {active_tool.replace('_', ' ').title()}\n\n"
    else:
        vt_text += "⚠️ **No tool selected**\nपहले एक tool enable करें!\n\n"
    
    vt_text += "Tool select करें (tick mark वाला active है):"
    
    await message.reply_text(vt_text, reply_markup=video_tools_buttons(active_tool))

@Client.on_message(filters.command("stop"))
async def stop_command(client: Client, message: Message):
    """Handle /stop command - clears tasks and data"""
    user_id = message.from_user.id

    await db.cancel_task(user_id)
    await db.clear_all_user_data(user_id)

    await message.reply_text(
        "🛑 **All Data Cleared**\n\n"
        "• Active tasks cancelled\n"
        "• Tool selections cleared\n"
        "• Temporary files removed\n\n"
        "Bot is still active. Use /hold to deactivate."
    )

@Client.on_message(filters.command("s") & filters.group)
async def show_tasks(client: Client, message: Message):
    """Show all running tasks in the group"""
    chat_id = message.chat.id

    if not await is_authorized_group(chat_id):
        return

    tasks = await db.get_all_active_tasks()

    if not tasks:
        await message.reply_text("📊 **No Active Tasks**\n\nकोई भी video processing task नहीं चल रहा है।")
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
    help_text = """
📚 **Video Tools Bot - Complete Guide**

**🎯 Commands:**
• `/start` - Bot activate करें
• `/hold` - Hold mode (processing band करें)
• `/us` - User Settings
• `/vt` - Video Tools menu
• `/stop` - सभी data clear करें
• `/s` - Active tasks देखें (groups)
• `/help` - यह help message

**1️⃣ User Settings (/us)**
अपनी preferences configure करें:
• **Send as**: Document/Video format
• **Thumbnail**: Custom thumbnail image
• **Filename**: Custom output filename
• **Metadata**: Video metadata on/off
• **Download Mode**: Telegram/URL downloads
• **Upload Mode**: Telegram/GoFile uploads

**2️⃣ Video Tools (/vt)**
Tool enable करें, फिर file भेजें:

🔗 **Video Merge**
   • Video+Video, Video+Audio, Video+Subs
   • Dual audio support
   
🎞️ **Encoding**
   • 1080p, 720p, 480p, 360p
   • HEVC (smaller files)
   
🔄 **Convert**
   • Document ↔ Video
   
©️ **Watermark**
   • Text या PNG image
   
✂️ **Trim**
   • Specific portions cut करें
   
🎬 **Sample**
   • 30/60/120/300 second samples
   
📊 **MediaInfo**
   • Professional file analysis

**📋 Important:**
• Settings database में save होती हैं
• एक बार tool enable करें, फिर files भेजें
• Download/Upload mode validate होता है

Owner: {Config.OWNER_ID}
"""
    await message.reply_text(help_text)
