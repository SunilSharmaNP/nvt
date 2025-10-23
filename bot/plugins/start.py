from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.helpers.buttons import main_menu_buttons
from bot.utils.helpers import is_admin, is_authorized_group
from config import Config

WELCOME_TEXT = """
👋 **Video Tools Bot में आपका स्वागत है!**

🎬 **Professional Video Processing**

यह bot आपको शक्तिशाली video editing tools प्रदान करता है:
• Video Encoding (Multiple Quality Presets)
• Video Merging (Video+Video, Video+Audio, Video+Subs)
• Format Conversion (Document↔Video)
• Watermarking
• Video Trimming
• Sample Generation
• MediaInfo Extraction

⚙️ **शुरू करने के लिए:**
1. पहले **User Settings** configure करें
2. **Video Tools** menu से tool चुनें
3. अपनी video file भेजें

📋 **जरूरी नोट:**
• एक समय में एक task
• Authorized groups में ही काम करता है
• Task शुरू करने से पहले settings set करें

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

    is_active = await db.is_user_active(user_id, chat_id)
    await db.set_user_active(user_id, chat_id, not is_active)

    if not is_active:
        await message.reply_text(
            f"✅ **Bot Activated for {message.from_user.mention}**\n\n"
            "🎬 अब आप सभी video tools का उपयोग कर सकते हैं!\n\n"
            "⚙️ **Quick Setup:**\n"
            "1. पहले User Settings configure करें\n"
            "2. Video Tools menu से tool चुनें\n"
            "3. अपनी files भेजें\n\n"
            "नीचे के buttons से शुरू करें:",
            reply_markup=main_menu_buttons()
        )
    else:
        await message.reply_text(
            f"⏸ **Bot Deactivated for {message.from_user.mention}**\n\n"
            "Bot अब hold mode में है।\n"
            "दोबारा activate करने के लिए /start उपयोग करें।"
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
            "सभी active tasks cancel कर दिए गए हैं।"
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
📚 **Video Tools Bot - Help Guide**

**Available Commands:**
• `/start` - Bot activate/deactivate करें
• `/stop` - Bot stop करें और tasks cancel करें
• `/s` - सभी running tasks देखें (groups only)
• `/help` - यह help message

**कैसे उपयोग करें:**

**1️⃣ User Settings**
Processing से पहले अपनी preferences configure करें:
• **Send as**: Document या Video
• **Thumbnail**: Custom thumbnail set करें
• **Filename**: Output filename customize करें
• **Metadata**: Enable/Disable करें
• **Download Mode**: Telegram या Direct URL
• **Upload Mode**: Telegram या GoFile server

**2️⃣ Video Tools**
7 शक्तिशाली tools में से चुनें:

🔗 **Video Merge**
   • Video + Video: Multiple videos merge करें
   • Video + Audio: Audio track replace/add करें
   • Video + Subtitles: Subtitle file add करें

🎞️ **Video Encoding**
   • Multiple quality presets (1080p, 720p, 480p, 360p)
   • HEVC encoding for smaller files
   • Custom encoding settings

🔄 **Convert**
   • Document to Video
   • Video to Document

©️ **Watermark**
   • Videos पर image watermark add करें

✂️ **Trim Video**
   • Video से specific portions cut करें

🎬 **Sample Video**
   • Sample clips generate करें

📊 **MediaInfo**
   • Detailed video information पाएं

**Important Notes:**
• एक समय में एक task per user
• Authorized groups में ही काम करता है
• Tasks शुरू करने से पहले User Settings set करें

और मदद चाहिए? Owner से संपर्क करें: {Config.OWNER_ID}
"""
    await message.reply_text(help_text)
    
