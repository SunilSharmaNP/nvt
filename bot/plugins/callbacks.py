from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from bot.database import db
from bot.helpers.buttons import *
from bot.utils.helpers import is_authorized_group, can_use_in_private
from config import Config

ABOUT_TEXT = f"""
🤖 **About Video Tools Bot**

**Version:** 3.0 (Professional Edition)
**Developer:** NVT Team

**Features:**
✅ Advanced Video Encoding
✅ Video Merging (Dual Audio Support)
✅ Format Conversion
✅ Text/Image Watermarking
✅ Video Trimming
✅ Sample Generation
✅ Professional MediaInfo
✅ URL Download Support
✅ Persistent User Settings

**Technology:**
• Pyrogram & Python
• FFmpeg for processing
• MongoDB for persistence
• Telegraph for MediaInfo
• Async/Await architecture

**Support:**
Owner ID: {Config.OWNER_ID}
"""

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    """Handle all callback queries"""
    user_id = query.from_user.id
    data = query.data

    # Ban check
    if await db.is_user_banned(user_id):
        await query.answer("❌ आप banned हैं।", show_alert=True)
        return

    # Authorization check for groups
    if query.message.chat.type != "private":
        if not await is_authorized_group(query.message.chat.id):
            await query.answer("⚠️ Unauthorized group!", show_alert=True)
            return

        if not await db.is_user_active(user_id, query.message.chat.id):
            await query.answer("⚠️ /start से bot activate करें!", show_alert=True)
            return
    else:
        # Private chat check
        if not await can_use_in_private(user_id):
            if data not in ["main_menu", "about", "help", "user_settings"]:
                await query.answer(
                    f"⚠️ Bot authorized groups में काम करता है!\nOwner: {Config.OWNER_ID}",
                    show_alert=True
                )
                return

    # Main Menu
    if data == "main_menu":
        await query.message.edit_text(
            "🏠 **Main Menu**\n\nOption चुनें:",
            reply_markup=main_menu_buttons()
        )

    # About
    elif data == "about":
        await query.message.edit_text(ABOUT_TEXT, reply_markup=back_to_main())

    # Help
    elif data == "help":
        help_text = """
📚 **Quick Guide**

**Setup:**
1. User Settings से preferences set करें
2. Video Tools से tool enable करें
3. File भेजें

**Important:**
• सभी settings database में save होती हैं
• एक tool enable करें, फिर files भेजें
• Download/Upload mode mismatch check होता है

Use /help for complete guide.
"""
        await query.message.edit_text(help_text, reply_markup=back_to_main())

    # User Settings Menu
    elif data == "user_settings":
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
        await query.message.edit_text(settings_text, reply_markup=user_settings_buttons())

    # Video Tools Menu
    elif data == "video_tools":
        user = await db.get_user(user_id)
        active_tool = user.get("video_tool_selected") if user else None
        
        vt_text = "🎬 **Video Tools Menu**\n\n"
        if active_tool:
            vt_text += f"✅ **Active:** {active_tool.replace('_', ' ').title()}\n\n"
        else:
            vt_text += "⚠️ पहले एक tool enable करें!\n\n"
        
        vt_text += "Tool select करें (✅ = active):"
        
        await query.message.edit_text(vt_text, reply_markup=video_tools_buttons(active_tool))

    # ========== USER SETTINGS HANDLERS ==========
    
    # Send As Setting
    elif data == "setting_send_as":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("send_as", "document") if user else "document"
        await query.message.edit_text(
            "📄 **Send As**\n\nProcessed files कैसे भेजें:",
            reply_markup=send_as_buttons(current)
        )

    elif data.startswith("sendas_"):
        option = data.split("_")[1]
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS.copy()) if user else Config.DEFAULT_SETTINGS.copy()
        settings["send_as"] = option
        await db.update_user_settings(user_id, settings)
        await query.answer(f"✅ {option.title()} में set किया गया")
        await query.message.edit_text(
            "📄 **Send As**\n\nProcessed files कैसे भेजें:",
            reply_markup=send_as_buttons(option)
        )

    # Thumbnail Setting
    elif data == "setting_thumbnail":
        await query.answer("अब एक photo भेजें thumbnail के लिए", show_alert=True)
        await query.message.reply_text(
            "🖼️ **Set Thumbnail**\n\n"
            "कृपया एक photo भेजें जो thumbnail के रूप में use होगी।\n"
            "Cancel करने के लिए /stop use करें।"
        )

    # Filename Setting  
    elif data == "setting_filename":
        await query.answer("अब custom filename text भेजें", show_alert=True)
        await query.message.reply_text(
            "📝 **Set Custom Filename**\n\n"
            "कृपया output filename भेजें (without extension)।\n"
            "Example: `MyVideo`, `Encoded_720p`\n\n"
            "Cancel करने के लिए /stop use करें।"
        )

    # Metadata Setting
    elif data == "setting_metadata":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("metadata", False) if user else False
        await query.message.edit_text(
            "📋 **Metadata Settings**\n\nMetadata enable/disable करें:",
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
            "📋 **Metadata Settings**\n\nMetadata enable/disable करें:",
            reply_markup=metadata_buttons(option)
        )

    # Download Mode Setting
    elif data == "setting_download_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("download_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬇️ **Download Mode**\n\n"
            "**Telegram:** Telegram से files download\n"
            "**URL:** Direct URL से download\n\n"
            "Select करें:",
            reply_markup=download_mode_buttons(current)
        )

    elif data.startswith("dlmode_"):
        option = data.split("_")[1]
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS.copy()) if user else Config.DEFAULT_SETTINGS.copy()
        settings["download_mode"] = option
        await db.update_user_settings(user_id, settings)
        await query.answer(f"✅ Download mode {option.upper()} set किया")
        await query.message.edit_text(
            "⬇️ **Download Mode**\n\nDownload source चुनें:",
            reply_markup=download_mode_buttons(option)
        )

    # Upload Mode Setting
    elif data == "setting_upload_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("upload_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬆️ **Upload Mode**\n\n"
            "**Telegram:** Direct upload to Telegram\n"
            "**GoFile:** Upload to GoFile server\n\n"
            "Select करें:",
            reply_markup=upload_mode_buttons(current)
        )

    elif data.startswith("upmode_"):
        option = data.split("_")[1]
        user = await db.get_user(user_id)
        settings = user.get("settings", Config.DEFAULT_SETTINGS.copy()) if user else Config.DEFAULT_SETTINGS.copy()
        settings["upload_mode"] = option
        await db.update_user_settings(user_id, settings)
        await query.answer(f"✅ Upload mode {option.title()} set किया")
        await query.message.edit_text(
            "⬆️ **Upload Mode**\n\nUpload destination चुनें:",
            reply_markup=upload_mode_buttons(option)
        )

    # ========== VIDEO TOOLS HANDLERS ==========

    # Merge Tool
    elif data == "tool_merge":
        await db.set_video_tool(user_id, "merge")
        user = await db.get_user(user_id)
        current_type = user.get("merge_type")
        
        await query.message.edit_text(
            "🔗 **Video Merge Tool**\n\n"
            "Merge type select करें (✅ = active):",
            reply_markup=merge_type_buttons(current_type)
        )
        await query.answer("✅ Merge tool enabled!")

    elif data.startswith("merge_"):
        merge_type = data.replace("merge_", "")
        await db.set_video_tool(user_id, "merge")
        await db.set_merge_type(user_id, merge_type)

        if merge_type == "video_video":
            instruction = "📹 2 या अधिक videos भेजें merge करने के लिए।"
        elif merge_type == "video_audio":
            instruction = "📹 पहले 1 video file भेजें, फिर 1 audio file (dual audio support)।"
        else:
            instruction = "📹 पहले 1 video file भेजें, फिर 1 subtitle file (.srt, .ass, .vtt)।"

        await query.message.edit_text(
            f"🔗 **{merge_type.replace('_', ' + ').title()}**\n\n{instruction}",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Merge type selected!")

    # Encoding Tool
    elif data == "tool_encoding":
        await db.set_video_tool(user_id, "encoding")
        user = await db.get_user(user_id)
        current_preset = user.get("encoding_settings", {}).get("preset_name") if user else None
        
        await query.message.edit_text(
            "🎞️ **Video Encoding Tool**\n\n"
            "Quality preset select करें (✅ = active):",
            reply_markup=encoding_quality_buttons(current_preset)
        )
        await query.answer("✅ Encoding tool enabled!")

    elif data.startswith("quality_"):
        quality = data.replace("quality_", "")
        await db.set_video_tool(user_id, "encoding")

        if quality == "custom":
            await query.message.edit_text(
                "⚙️ **Custom Encoding**\n\n"
                "Default presets के साथ आगे बढ़ें।\n"
                "अब video भेजें:",
                reply_markup=encoding_settings_buttons()
            )
            await db.set_encoding_settings(user_id, {"preset_name": "custom"})
        else:
            preset = Config.VIDEO_PRESETS.get(quality, Config.VIDEO_PRESETS["720p"])
            preset["preset_name"] = quality
            await db.set_encoding_settings(user_id, preset)

            await query.message.edit_text(
                f"✅ **{quality.upper()} Selected**\n\n"
                "📹 अब video file भेजें encoding के लिए।",
                reply_markup=back_to_video_tools()
            )
        await query.answer(f"✅ {quality.upper()} preset selected!")

    elif data == "enc_done":
        await query.message.edit_text(
            "✅ **Settings Configured**\n\n"
            "📹 अब video file भेजें।",
            reply_markup=back_to_video_tools()
        )

    # Convert Tool
    elif data == "tool_convert":
        await db.set_video_tool(user_id, "convert")
        user = await db.get_user(user_id)
        current_mode = user.get("convert_mode", "to_document")
        
        await query.message.edit_text(
            "🔄 **Convert Tool**\n\n"
            "Convert mode select करें (✅ = active):",
            reply_markup=convert_mode_buttons(current_mode)
        )
        await query.answer("✅ Convert tool enabled!")

    elif data.startswith("convert_"):
        mode = data.replace("convert_", "")
        await db.set_convert_mode(user_id, mode)
        
        if mode == "to_document":
            instruction = "📄 Video file भेजें document में convert करने के लिए।"
        else:
            instruction = "🎥 Document file भेजें video में convert करने के लिए।"
        
        await query.message.edit_text(
            f"🔄 **Convert: {mode.replace('_', ' ').title()}**\n\n{instruction}",
            reply_markup=back_to_video_tools()
        )
        await query.answer(f"✅ Convert mode: {mode}")

    # Watermark Tool
    elif data == "tool_watermark":
        await db.set_video_tool(user_id, "watermark")
        user = await db.get_user(user_id)
        current_type = user.get("watermark_type")
        
        await query.message.edit_text(
            "©️ **Watermark Tool**\n\n"
            "Watermark type select करें (✅ = active):",
            reply_markup=watermark_type_buttons(current_type)
        )
        await query.answer("✅ Watermark tool enabled!")

    elif data == "wm_type_text":
        await db.set_watermark_type(user_id, "text")
        await query.answer("अब watermark text भेजें", show_alert=True)
        await query.message.reply_text(
            "📝 **Text Watermark**\n\n"
            "कृपया watermark text भेजें।\n"
            "Example: `© MyChannel` या `@YourUsername`"
        )

    elif data == "wm_type_image":
        await db.set_watermark_type(user_id, "image")
        await query.answer("अब PNG image भेजें", show_alert=True)
        await query.message.reply_text(
            "🖼️ **Image Watermark**\n\n"
            "कृपया PNG image भेजें (transparent background recommended)।"
        )

    elif data == "wm_position_menu":
        user = await db.get_user(user_id)
        current_pos = user.get("watermark_position", "topright")
        await query.message.edit_text(
            "📍 **Watermark Position**\n\nPosition select करें:",
            reply_markup=watermark_position_buttons(current_pos)
        )

    elif data.startswith("wm_pos_"):
        position = data.replace("wm_pos_", "")
        await db.set_watermark_position(user_id, position)
        await query.answer(f"✅ Position: {position}")
        await query.message.edit_text(
            f"✅ **Position Set: {position.title()}**\n\n"
            "अब video भेजें watermark add करने के लिए।",
            reply_markup=back_to_video_tools()
        )

    # Trim Tool
    elif data == "tool_trim":
        await db.set_video_tool(user_id, "trim")
        await query.message.edit_text(
            "✂️ **Trim Video Tool**\n\n"
            "📹 Video file भेजें।\n"
            "फिर मैं आपसे trim details पूछूंगा।\n\n"
            "**Format Example:**\n"
            "`00:00:10-00:00:30` (10 sec to 30 sec)",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Trim tool enabled! Video भेजें।")

    # Sample Tool
    elif data == "tool_sample":
        await db.set_video_tool(user_id, "sample")
        user = await db.get_user(user_id)
        current_duration = user.get("sample_duration", 30)
        
        await query.message.edit_text(
            "🎬 **Sample Video Tool**\n\n"
            "Sample duration select करें (✅ = active):",
            reply_markup=sample_duration_buttons(current_duration)
        )
        await query.answer("✅ Sample tool enabled!")

    elif data.startswith("sample_"):
        duration = int(data.replace("sample_", ""))
        await db.set_sample_duration(user_id, duration)
        await query.message.edit_text(
            f"✅ **{duration}s Sample Selected**\n\n"
            "📹 अब video file भेजें {duration}-second sample generate करने के लिए।",
            reply_markup=back_to_video_tools()
        )
        await query.answer(f"✅ {duration}s sample selected!")

    # MediaInfo Tool
    elif data == "tool_mediainfo":
        await db.set_video_tool(user_id, "mediainfo")
        await query.message.edit_text(
            "📊 **MediaInfo Tool**\n\n"
            "📹 Video file भेजें professional MediaInfo के लिए।\n"
            "Graph के साथ detailed analysis milega।",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ MediaInfo tool enabled! Video भेजें।")

    # Cancel Operation
    elif data == "cancel_operation":
        await db.clear_temp_files(user_id)
        await query.message.edit_text(
            "❌ **Operation Cancelled**\n\n"
            "Temporary data cleared।",
            reply_markup=main_menu_buttons()
        )
        await query.answer("Cancelled")
