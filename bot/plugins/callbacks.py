from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from bot.database import db
from bot.helpers.buttons import *
from bot.utils.helpers import is_authorized_group, can_use_in_private
from config import Config

ABOUT_TEXT = f"""
🤖 **About Video Tools Bot**

**Version:** 3.0 (Professional Edition)
**Developer:** Professional Bot Development Team

**Features:**
✅ Advanced Video Encoding
✅ Video Merging (Video+Video, Video+Audio, Video+Subs)
✅ Format Conversion
✅ Watermark Addition
✅ Video Trimming
✅ Sample Generation
✅ Detailed MediaInfo

**Technology:**
• Built with Pyrogram & Python
• FFmpeg for video processing
• MongoDB for data management
• Async processing

**Support:**
Owner ID: `{Config.OWNER_ID}`
"""

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    """Handle all callback queries"""
    user_id = query.from_user.id
    data = query.data
    
    if await db.is_user_banned(user_id):
        await query.answer("❌ You are banned.", show_alert=True)
        return
    
    # Check authorization
    if query.message.chat.type != "private":
        if not await is_authorized_group(query.message.chat.id):
            await query.answer("⚠️ Unauthorized group!", show_alert=True)
            return
        
        if not await db.is_user_active(user_id, query.message.chat.id):
            await query.answer("⚠️ Activate bot using /start!", show_alert=True)
            return
    else:
        if not await can_use_in_private(user_id):
            if data not in ["main_menu", "about", "help", "user_settings", "stop_bot"]:
                await query.answer(
                    f"⚠️ Bot works in authorized groups!\\nContact owner {Config.OWNER_ID}.",
                    show_alert=True
                )
                return
    
    # Main navigation
    if data == "main_menu":
        await query.message.edit_text(
            "🏠 **Main Menu**\\n\\nChoose an option:",
            reply_markup=main_menu_buttons()
        )
    
    elif data == "about":
        await query.message.edit_text(ABOUT_TEXT, reply_markup=back_to_main())
    
    elif data == "help":
        help_text = """
📚 **How to Use**

**Step 1: Configure Settings** ⚙️
Go to User Settings and configure your preferences

**Step 2: Select Tool** 🎬
Choose a tool from Video Tools menu

**Step 3: Send Files** 📤
Send the required files after tool selection

**Important:**
• Configure User Settings first
• One task at a time
• Private chat has limited features (use groups)
"""
        await query.message.edit_text(help_text, reply_markup=back_to_main())
    
    elif data == "user_settings":
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS) if user else Config.DEFAULT_SETTINGS
        
        settings_text = f"""
⚙️ **Your Current Settings**

📄 **Send as:** `{settings.get('send_as', 'document').title()}`
🖼️ **Thumbnail:** `{'Set' if settings.get('thumbnail') else 'Not Set'}`
📝 **Filename:** `{settings.get('filename', 'default').title()}`
📋 **Metadata:** `{'Enabled' if settings.get('metadata') else 'Disabled'}`
⬇️ **Download Mode:** `{settings.get('download_mode', 'telegram').upper()}`
⬆️ **Upload Mode:** `{settings.get('upload_mode', 'telegram').title()}`

Click below to change a setting:
"""
        await query.message.edit_text(settings_text, reply_markup=user_settings_buttons())
    
    elif data == "video_tools":
        await query.message.edit_text(
            "🎬 **Video Tools Menu**\\n\\nSelect a tool:",
            reply_markup=video_tools_buttons()
        )
    
    elif data == "stop_bot":
        await db.cancel_task(user_id)
        await db.clear_temp_files(user_id)
        
        if query.message.chat.type != "private":
            await db.set_user_active(user_id, query.message.chat.id, False)
        
        await query.message.edit_text(
            "🛑 **Bot Stopped**\\n\\n"
            "✅ Tasks cancelled\\n"
            "✅ Files cleared\\n"
            "✅ Hold mode set\\n\\n"
            "Use /start to activate."
        )
    
    # User Settings Callbacks
    elif data == "setting_send_as":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("send_as", "document") if user else "document"
        await query.message.edit_text(
            "📄 **Send As**\\n\\nHow to send processed files:",
            reply_markup=send_as_buttons(current)
        )
    
    elif data.startswith("sendas_"):
        option = data.split("_")[1]
        await db.update_user_setting(user_id, "send_as", option)
        await query.answer(f"✅ Set to {option.title()}")
        await query.message.edit_text(
            "📄 **Send As**\\n\\nHow to send processed files:",
            reply_markup=send_as_buttons(option)
        )
    
    elif data == "setting_metadata":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("metadata", False) if user else False
        await query.message.edit_text(
            "📋 **Metadata Settings**\\n\\nEnable or disable metadata:",
            reply_markup=metadata_buttons(current)
        )
    
    elif data.startswith("metadata_"):
        option = data.split("_")[1] == "true"
        await db.update_user_setting(user_id, "metadata", option)
        await query.answer(f"✅ Metadata {'Enabled' if option else 'Disabled'}")
        await query.message.edit_text(
            "📋 **Metadata Settings**\\n\\nEnable or disable metadata:",
            reply_markup=metadata_buttons(option)
        )
    
    elif data == "setting_download_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("download_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬇️ **Download Mode**\\n\\nSelect download source:",
            reply_markup=download_mode_buttons(current)
        )
    
    elif data.startswith("dlmode_"):
        option = data.split("_")[1]
        await db.update_user_setting(user_id, "download_mode", option)
        await query.answer(f"✅ Download mode set to {option.upper()}")
        await query.message.edit_text(
            "⬇️ **Download Mode**\\n\\nSelect download source:",
            reply_markup=download_mode_buttons(option)
        )
    
    elif data == "setting_upload_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("upload_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬆️ **Upload Mode**\\n\\nSelect upload destination:",
            reply_markup=upload_mode_buttons(current)
        )
    
    elif data.startswith("upmode_"):
        option = data.split("_")[1]
        await db.update_user_setting(user_id, "upload_mode", option)
        await query.answer(f"✅ Upload mode set to {option.title()}")
        await query.message.edit_text(
            "⬆️ **Upload Mode**\\n\\nSelect upload destination:",
            reply_markup=upload_mode_buttons(option)
        )
    
    # Tool selection callbacks  
    elif data == "tool_encoding":
        await db.set_video_tool(user_id, "encoding")
        await query.message.edit_text(
            "🎞️ **Video Encoding**\\n\\nSelect quality preset:",
            reply_markup=encoding_quality_buttons()
        )
    
    elif data.startswith("quality_"):
        quality = data.replace("quality_", "")
        if quality in Config.VIDEO_PRESETS:
            preset = Config.VIDEO_PRESETS[quality].copy()
            preset["preset_name"] = quality
            await db.set_encoding_settings(user_id, preset)
            await query.answer(f"✅ {quality.upper()} selected!")
            await query.message.edit_text(
                f"✅ **{quality.upper()} Selected**\\n\\n"
                "📹 Now send a video file to encode.",
                reply_markup=back_to_video_tools()
            )
    
    elif data == "tool_merge":
        await db.set_video_tool(user_id, "merge")
        await query.message.edit_text(
            "🔗 **Video Merge**\\n\\nSelect merge type:",
            reply_markup=merge_type_buttons()
        )
    
    elif data.startswith("merge_"):
        merge_type = data.replace("merge_", "")
        await db.set_merge_type(user_id, merge_type)
        
        instructions = {
            "video_video": "📹 Send 2 or more videos to merge.",
            "video_audio": "📹 First send 1 video file, then 1 audio file.",
            "video_subs": "📹 First send 1 video file, then 1 subtitle file (.srt, .ass, .vtt)."
        }
        
        await query.message.edit_text(
            f"🔗 **{merge_type.replace('_', ' + ').title()}**\\n\\n{instructions.get(merge_type, 'Send files')}",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Merge mode selected! Send files.")
    
    elif data == "tool_mediainfo":
        await db.set_video_tool(user_id, "mediainfo")
        await query.message.edit_text(
            "📊 **MediaInfo**\\n\\n"
            "📹 Send a video file to extract detailed information.",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ MediaInfo mode selected! Send video.")
    
    elif data == "tool_trim":
        await db.set_video_tool(user_id, "trim")
        await query.message.edit_text(
            "✂️ **Trim Video**\\n\\n"
            "📹 Send a video file first.\\n"
            "Then send trim times in format: `start:end` (in seconds)\\n\\n"
            "**Example:** `10:120` (trim from 10s to 120s)",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Trim mode selected!")
    
    elif data == "tool_sample":
        await db.set_video_tool(user_id, "sample")
        await query.message.edit_text(
            "🎬 **Sample Video**\\n\\nSelect sample duration:",
            reply_markup=sample_duration_buttons()
        )
    
    elif data.startswith("sample_"):
        duration = data.replace("sample_", "")
        await db.set_sample_duration(user_id, duration)
        await query.answer(f"✅ Sample duration: {Config.SAMPLE_DURATIONS[duration]}s")
        await query.message.edit_text(
            f"🎬 **Sample Video - {duration.upper()}**\\n\\n"
            f"⏱️ Duration: {Config.SAMPLE_DURATIONS[duration]} seconds\\n\\n"
            "📹 Now send a video file to generate sample.",
            reply_markup=back_to_video_tools()
        )
    
    elif data == "tool_watermark":
        await db.set_video_tool(user_id, "watermark")
        await query.message.edit_text(
            "©️ **Add Watermark**\\n\\nSelect watermark position:",
            reply_markup=watermark_position_buttons()
        )
    
    elif data.startswith("wm_"):
        position = data.replace("wm_", "")
        await db.set_watermark_position(user_id, position)
        await query.answer(f"✅ Position: {position.title()}")
        await query.message.edit_text(
            f"©️ **Watermark - {position.upper()}**\\n\\n"
            "📹 First send a video file\\n"
            "📄 Then send a watermark image (PNG/JPG)",
            reply_markup=back_to_video_tools()
        )
    
    elif data == "setting_thumbnail":
        await query.answer("📸 Send a photo to set as thumbnail!", show_alert=True)
        await query.message.edit_text(
            "🖼️ **Set Thumbnail**\\n\\n"
            "📸 Send a photo to use as thumbnail for all uploads\\n"
            "❌ Send /clearthumb to remove thumbnail\\n\\n"
            "⚠️ This will be used for all future uploads.",
            reply_markup=back_to_main()
        )
    
    elif data == "setting_filename":
        await query.answer("✏️ Send new filename format!", show_alert=True)
        await query.message.edit_text(
            "📝 **Filename Format**\\n\\n"
            "✏️ Send your desired filename format\\n"
            "🔹 Use `{original}` for original name\\n"
            "🔹 Use `{time}` for timestamp\\n\\n"
            "**Examples:**\\n"
            "`MyVideo_{time}` → MyVideo_1234567890.mp4\\n"
            "`Encoded_{original}` → Encoded_video.mp4\\n\\n"
            "Send `/defaultname` to reset to default",
            reply_markup=back_to_main()
        )
    
    else:
        await query.answer("⚠️ Feature coming soon!", show_alert=True)
