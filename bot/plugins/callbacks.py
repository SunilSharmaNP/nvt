from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from bot.database import db
from bot.helpers.buttons import *
from bot.utils.helpers import is_authorized_group, can_use_in_private
from config import Config

ABOUT_TEXT = """
🤖 **About Video Tools Bot**

**Version:** 2.0
**Developer:** Professional Bot Development Team

**Features:**
✅ Advanced Video Encoding with multiple presets
✅ Video Merging (Video+Video, Video+Audio, Video+Subs)
✅ Format Conversion (Document ↔ Video)
✅ Watermark Addition
✅ Video Trimming
✅ Sample Generation
✅ Detailed MediaInfo

**Technology:**
• Built with Pyrogram & Python
• FFmpeg for video processing
• MongoDB for data management
• Async processing for efficiency

**Key Capabilities:**
• Multiple quality presets (1080p, 720p, 480p, 360p)
• HEVC encoding support
• Custom encoding parameters
• Flexible upload options (Telegram/GoFile)
• Smart file management
• User preference system

**Usage Policy:**
• Works in authorized groups only
• One task per user at a time
• Multiple users can process simultaneously
• Private chat limited to admins

**Support:**
For issues or feature requests, contact:
Owner ID: {Config.OWNER_ID}
"""

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    """Handle all callback queries"""
    user_id = query.from_user.id
    data = query.data
    
    # Check if user is banned
    if await db.is_user_banned(user_id):
        await query.answer("❌ You are banned from using this bot.", show_alert=True)
        return
    
    # Check authorization for non-private chats
    if query.message.chat.type != "private":
        if not await is_authorized_group(query.message.chat.id):
            await query.answer("⚠️ Unauthorized group!", show_alert=True)
            return
        
        # Check if user is active in this group
        if not await db.is_user_active(user_id, query.message.chat.id):
            await query.answer("⚠️ Use /start first to activate the bot!", show_alert=True)
            return
    else:
        # Private chat - check if admin
        if not await can_use_in_private(user_id):
            if data not in ["main_menu", "about", "help", "user_settings", "stop_bot"]:
                await query.answer(
                    "⚠️ This bot works only in authorized groups!\n"
                    f"Contact owner {Config.OWNER_ID} to get access.",
                    show_alert=True
                )
                return
    
    # Main menu callbacks
    if data == "main_menu":
        await query.message.edit_text(
            "🏠 **Main Menu**\n\nChoose an option:",
            reply_markup=main_menu_buttons()
        )
    
    elif data == "about":
        await query.message.edit_text(
            ABOUT_TEXT,
            reply_markup=back_to_main()
        )
    
    elif data == "help":
        help_text = """
📚 **How to Use Video Tools Bot**

**Step 1: Configure Settings** ⚙️
Go to User Settings and configure:
• Output format (Document/Video)
• Thumbnail (optional)
• Custom filename (optional)
• Metadata settings
• Download source (Telegram/URL)
• Upload destination (Telegram/GoFile)

**Step 2: Select Tool** 🎬
Choose from Video Tools menu:
• Video Merge - Combine videos or add audio/subs
• Video Encoding - Compress/encode with quality presets
• Convert - Change between document and video
• Watermark - Add logo/watermark to video
• Trim - Cut specific portions
• Sample - Generate preview clips
• MediaInfo - Get file details

**Step 3: Send Files** 📤
After selecting a tool:
• Send the required file(s)
• Bot will validate and process
• Receive your processed file!

**Important:**
• Set User Settings before starting
• One task at a time per user
• Private chat limited (use in groups)
• For DDL downloads, set download mode to URL

Need assistance? Contact: {Config.OWNER_ID}
"""
        await query.message.edit_text(
            help_text,
            reply_markup=back_to_main()
        )
    
    elif data == "user_settings":
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS) if user else Config.DEFAULT_SETTINGS
        
        settings_text = f"""
⚙️ **Your Current Settings**

📄 **Send as:** {settings.get('send_as', 'document').title()}
🖼️ **Thumbnail:** {'Set' if settings.get('thumbnail') else 'Not Set'}
📝 **Filename:** {settings.get('filename', 'default').title()}
📋 **Metadata:** {'Enabled' if settings.get('metadata') else 'Disabled'}
⬇️ **Download Mode:** {settings.get('download_mode', 'telegram').upper()}
⬆️ **Upload Mode:** {settings.get('upload_mode', 'telegram').title()}

Click below to change any setting:
"""
        await query.message.edit_text(
            settings_text,
            reply_markup=user_settings_buttons()
        )
    
    elif data == "video_tools":
        await query.message.edit_text(
            "🎬 **Video Tools Menu**\n\nSelect a tool to use:",
            reply_markup=video_tools_buttons()
        )
    
    elif data == "stop_bot":
        await db.cancel_task(user_id)
        await db.clear_temp_files(user_id)
        
        if query.message.chat.type != "private":
            await db.set_user_active(user_id, query.message.chat.id, False)
        
        await query.message.edit_text(
            "🛑 **Bot Stopped**\n\n"
            "✅ All tasks cancelled\n"
            "✅ Temporary files cleared\n"
            "✅ Bot set to hold mode\n\n"
            "Use /start to activate again."
        )
    
    # User Settings callbacks
    elif data == "setting_send_as":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("send_as", "document") if user else "document"
        await query.message.edit_text(
            "📄 **Send As**\n\nChoose how to send processed files:",
            reply_markup=send_as_buttons(current)
        )
    
    elif data.startswith("sendas_"):
        option = data.split("_")[1]
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS.copy()) if user else Config.DEFAULT_SETTINGS.copy()
        settings["send_as"] = option
        await db.update_user_settings(user_id, settings)
        await query.answer(f"✅ Set to {option.title()}")
        await query.message.edit_text(
            "📄 **Send As**\n\nChoose how to send processed files:",
            reply_markup=send_as_buttons(option)
        )
    
    elif data == "setting_thumbnail":
        await query.message.edit_text(
            "🖼️ **Set Thumbnail**\n\n"
            "Send me an image to use as thumbnail for your videos.\n\n"
            "Send /cancel to go back.",
            reply_markup=back_to_main()
        )
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"awaiting_thumbnail": True}}
        )
    
    elif data == "setting_filename":
        await query.message.edit_text(
            "📝 **Set Custom Filename**\n\n"
            "Send me the filename pattern you want to use.\n"
            "Use `{original}` to keep original filename.\n\n"
            "Example: `MyVideo_{original}`\n\n"
            "Send /cancel to go back.",
            reply_markup=back_to_main()
        )
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"awaiting_filename": True}}
        )
    
    elif data == "setting_metadata":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("metadata", False) if user else False
        await query.message.edit_text(
            "📋 **Metadata Settings**\n\nEnable or disable metadata in output files:",
            reply_markup=metadata_buttons(current)
        )
    
    elif data.startswith("metadata_"):
        option = data.split("_")[1] == "true"
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS.copy()) if user else Config.DEFAULT_SETTINGS.copy()
        settings["metadata"] = option
        await db.update_user_settings(user_id, settings)
        await query.answer(f"✅ Metadata {'Enabled' if option else 'Disabled'}")
        await query.message.edit_text(
            "📋 **Metadata Settings**\n\nEnable or disable metadata in output files:",
            reply_markup=metadata_buttons(option)
        )
    
    elif data == "setting_download_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("download_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬇️ **Download Mode**\n\nChoose download source:",
            reply_markup=download_mode_buttons(current)
        )
    
    elif data.startswith("dlmode_"):
        option = data.split("_")[1]
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS.copy()) if user else Config.DEFAULT_SETTINGS.copy()
        settings["download_mode"] = option
        await db.update_user_settings(user_id, settings)
        await query.answer(f"✅ Download mode set to {option.upper()}")
        await query.message.edit_text(
            "⬇️ **Download Mode**\n\nChoose download source:",
            reply_markup=download_mode_buttons(option)
        )
    
    elif data == "setting_upload_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("upload_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬆️ **Upload Mode**\n\nChoose upload destination:",
            reply_markup=upload_mode_buttons(current)
        )
    
    elif data.startswith("upmode_"):
        option = data.split("_")[1]
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS.copy()) if user else Config.DEFAULT_SETTINGS.copy()
        settings["upload_mode"] = option
        await db.update_user_settings(user_id, settings)
        await query.answer(f"✅ Upload mode set to {option.title()}")
        await query.message.edit_text(
            "⬆️ **Upload Mode**\n\nChoose upload destination:",
            reply_markup=upload_mode_buttons(option)
        )
    
    # Video Tools callbacks
    elif data == "tool_merge":
        await db.set_video_tool(user_id, "merge")
        await query.message.edit_text(
            "🔗 **Video Merge**\n\nSelect merge type:",
            reply_markup=merge_type_buttons()
        )
    
    elif data.startswith("merge_"):
        merge_type = data.replace("merge_", "")
        await db.set_video_tool(user_id, "merge")
        await db.set_merge_type(user_id, merge_type)
        
        if merge_type == "video_video":
            instruction = "📹 Send at least 2 videos to merge them together."
        elif merge_type == "video_audio":
            instruction = "📹 Send 1 video file, then 1 audio file to merge."
        else:  # video_subs
            instruction = "📹 Send 1 video file, then 1 subtitle file (.srt, .ass, .vtt) to merge."
        
        await query.message.edit_text(
            f"🔗 **{merge_type.replace('_', ' + ').title()}**\n\n{instruction}",
            reply_markup=back_to_main()
        )
        await query.answer("✅ Merge mode selected! Send files now.")
    
    elif data == "tool_encoding":
        await db.set_video_tool(user_id, "encoding")
        await query.message.edit_text(
            "🎞️ **Video Encoding**\n\nSelect quality preset:",
            reply_markup=encoding_quality_buttons()
        )
    
    elif data.startswith("quality_"):
        quality = data.replace("quality_", "")
        
        if quality == "custom":
            await query.message.edit_text(
                "⚙️ **Custom Encoding Settings**\n\n"
                "Configure your custom encoding parameters:",
                reply_markup=encoding_settings_buttons()
            )
            await db.set_encoding_settings(user_id, {"preset_name": "custom"})
        else:
            preset = Config.VIDEO_PRESETS.get(quality, Config.VIDEO_PRESETS["720p"])
            preset["preset_name"] = quality
            await db.set_encoding_settings(user_id, preset)
            
            await query.message.edit_text(
                f"✅ **{quality.upper()} Selected**\n\n"
                "You can customize encoding settings or start directly.\n\n"
                "📹 Send a video file to start encoding.",
                reply_markup=encoding_settings_buttons()
            )
            await query.answer(f"✅ {quality.upper()} preset selected!")
    
    elif data.startswith("enc_"):
        await query.answer("⚙️ Send the value for this setting", show_alert=True)
        setting_name = data.replace("enc_", "")
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {f"awaiting_enc_{setting_name}": True}}
        )
    
    elif data == "enc_done":
        user = await db.get_user(user_id)
        enc_settings = user.get("encoding_settings")
        
        if not enc_settings:
            await query.answer("⚠️ Please select a quality preset first!", show_alert=True)
            return
        
        await query.message.edit_text(
            "✅ **Encoding Settings Configured**\n\n"
            "📹 Send a video file to start encoding.",
            reply_markup=back_to_main()
        )
        await query.answer("✅ Ready to encode! Send a video.")
    
    elif data == "tool_convert":
        await db.set_video_tool(user_id, "convert")
        await query.message.edit_text(
            "🔄 **Convert**\n\n"
            "📹 Send a video (to convert to document) or\n"
            "📄 Send a document (to convert to video)",
            reply_markup=back_to_main()
        )
        await query.answer("✅ Convert mode selected! Send a file.")
    
    elif data == "tool_watermark":
        await db.set_video_tool(user_id, "watermark")
        await query.message.edit_text(
            "©️ **Add Watermark**\n\n"
            "📹 Send a video file first, then send the watermark image.",
            reply_markup=back_to_main()
        )
        await query.answer("✅ Watermark mode selected! Send files.")
    
    elif data == "tool_trim":
        await db.set_video_tool(user_id, "trim")
        await query.message.edit_text(
            "✂️ **Trim Video**\n\n"
            "📹 Send a video file to trim.",
            reply_markup=back_to_main()
        )
        await query.answer("✅ Trim mode selected! Send a video.")
    
    elif data == "tool_sample":
        await db.set_video_tool(user_id, "sample")
        await query.message.edit_text(
            "🎬 **Generate Sample**\n\n"
            "📹 Send a video file to generate a 30-second sample.",
            reply_markup=back_to_main()
        )
        await query.answer("✅ Sample mode selected! Send a video.")
    
    elif data == "tool_mediainfo":
        await db.set_video_tool(user_id, "mediainfo")
        await query.message.edit_text(
            "📊 **MediaInfo**\n\n"
            "📹 Send a video file to get detailed information.",
            reply_markup=back_to_main()
        )
        await query.answer("✅ MediaInfo mode selected! Send a video.")
    
    await query.answer()
