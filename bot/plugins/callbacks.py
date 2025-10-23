from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from bot.database import db
from bot.helpers.buttons import *
from bot.utils.helpers import is_authorized_group, can_use_in_private
from config import Config

ABOUT_TEXT = f"""
🤖 **About Video Tools Bot**

**Version:** 2.0 (Fixed & Enhanced)
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
Owner ID: {Config.OWNER_ID}
"""

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    """Handle all callback queries"""
    user_id = query.from_user.id
    data = query.data

    if await db.is_user_banned(user_id):
        await query.answer("❌ आप banned हैं।", show_alert=True)
        return

    if query.message.chat.type != "private":
        if not await is_authorized_group(query.message.chat.id):
            await query.answer("⚠️ Unauthorized group!", show_alert=True)
            return

        if not await db.is_user_active(user_id, query.message.chat.id):
            await query.answer("⚠️ /start से bot activate करें!", show_alert=True)
            return
    else:
        if not await can_use_in_private(user_id):
            if data not in ["main_menu", "about", "help", "user_settings", "stop_bot"]:
                await query.answer(
                    f"⚠️ Bot authorized groups में काम करता है!\\nOwner {Config.OWNER_ID} से संपर्क करें।",
                    show_alert=True
                )
                return

    if data == "main_menu":
        await query.message.edit_text(
            "🏠 **Main Menu**\\n\\nOption चुनें:",
            reply_markup=main_menu_buttons()
        )

    elif data == "about":
        await query.message.edit_text(ABOUT_TEXT, reply_markup=back_to_main())

    elif data == "help":
        help_text = """
📚 **कैसे उपयोग करें**

**Step 1: Settings Configure करें** ⚙️
User Settings में जाएं और configure करें

**Step 2: Tool Select करें** 🎬
Video Tools menu से tool चुनें

**Step 3: Files भेजें** 📤
Tool select करने के बाद required files भेजें

**Important:**
• पहले User Settings set करें
• एक समय में एक task
• Private chat limited (groups में use करें)
"""
        await query.message.edit_text(help_text, reply_markup=back_to_main())

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

नीचे से setting बदलें:
"""
        await query.message.edit_text(settings_text, reply_markup=user_settings_buttons())

    elif data == "video_tools":
        await query.message.edit_text(
            "🎬 **Video Tools Menu**\\n\\nTool select करें:",
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
            "/start से activate करें।"
        )

    elif data == "setting_send_as":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("send_as", "document") if user else "document"
        await query.message.edit_text(
            "📄 **Send As**\\n\\nProcessed files कैसे भेजें:",
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
            "📄 **Send As**\\n\\nProcessed files कैसे भेजें:",
            reply_markup=send_as_buttons(option)
        )

    elif data == "setting_metadata":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("metadata", False) if user else False
        await query.message.edit_text(
            "📋 **Metadata Settings**\\n\\nMetadata enable/disable करें:",
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
            "📋 **Metadata Settings**\\n\\nMetadata enable/disable करें:",
            reply_markup=metadata_buttons(option)
        )

    elif data == "setting_download_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("download_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬇️ **Download Mode**\\n\\nDownload source चुनें:",
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
            "⬇️ **Download Mode**\\n\\nDownload source चुनें:",
            reply_markup=download_mode_buttons(option)
        )

    elif data == "setting_upload_mode":
        user = await db.get_user(user_id)
        current = user.get("settings", {}).get("upload_mode", "telegram") if user else "telegram"
        await query.message.edit_text(
            "⬆️ **Upload Mode**\\n\\nUpload destination चुनें:",
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
            "⬆️ **Upload Mode**\\n\\nUpload destination चुनें:",
            reply_markup=upload_mode_buttons(option)
        )

    elif data == "tool_merge":
        await db.set_video_tool(user_id, "merge")
        await query.message.edit_text(
            "🔗 **Video Merge**\\n\\nMerge type select करें:",
            reply_markup=merge_type_buttons()
        )

    elif data.startswith("merge_"):
        merge_type = data.replace("merge_", "")
        await db.set_video_tool(user_id, "merge")
        await db.set_merge_type(user_id, merge_type)

        if merge_type == "video_video":
            instruction = "📹 2 या अधिक videos भेजें merge करने के लिए।"
        elif merge_type == "video_audio":
            instruction = "📹 पहले 1 video file भेजें, फिर 1 audio file।"
        else:
            instruction = "📹 पहले 1 video file भेजें, फिर 1 subtitle file (.srt, .ass, .vtt)।"

        await query.message.edit_text(
            f"🔗 **{merge_type.replace('_', ' + ').title()}**\\n\\n{instruction}",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Merge mode selected! Files भेजें।")

    elif data == "tool_encoding":
        await db.set_video_tool(user_id, "encoding")
        await query.message.edit_text(
            "🎞️ **Video Encoding**\\n\\nQuality preset select करें:",
            reply_markup=encoding_quality_buttons()
        )

    elif data.startswith("quality_"):
        quality = data.replace("quality_", "")

        if quality == "custom":
            await query.message.edit_text(
                "⚙️ **Custom Encoding Settings**\\n\\nCustom parameters configure करें:",
                reply_markup=encoding_settings_buttons()
            )
            await db.set_encoding_settings(user_id, {"preset_name": "custom"})
        else:
            preset = Config.VIDEO_PRESETS.get(quality, Config.VIDEO_PRESETS["720p"])
            preset["preset_name"] = quality
            await db.set_encoding_settings(user_id, preset)

            await query.message.edit_text(
                f"✅ **{quality.upper()} Selected**\\n\\n"
                "📹 अब video file भेजें encoding के लिए।",
                reply_markup=encoding_settings_buttons()
            )
            await query.answer(f"✅ {quality.upper()} preset selected!")

    elif data == "enc_done":
        user = await db.get_user(user_id)
        enc_settings = user.get("encoding_settings")

        if not enc_settings:
            await query.answer("⚠️ पहले quality preset select करें!", show_alert=True)
            return

        await query.message.edit_text(
            "✅ **Encoding Settings Configured**\\n\\n"
            "📹 अब video file भेजें encoding के लिए।",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Ready! Video file भेजें।")

    elif data == "tool_convert":
        await db.set_video_tool(user_id, "convert")
        await query.message.edit_text(
            "🔄 **Convert**\\n\\n"
            "📹 Video भेजें (document में convert करने के लिए) या\\n"
            "📄 Document भेजें (video में convert करने के लिए)",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Convert mode selected! File भेजें।")

    elif data == "tool_watermark":
        await db.set_video_tool(user_id, "watermark")
        await query.message.edit_text(
            "©️ **Add Watermark**\\n\\n"
            "Watermark position select करें:",
            reply_markup=watermark_position_buttons()
        )

    elif data.startswith("wm_"):
        position = data.replace("wm_", "")
        await db.set_watermark_position(user_id, position)
        await query.message.edit_text(
            f"©️ **Watermark Position: {position.title()}**\\n\\n"
            "📹 पहले video file भेजें, फिर watermark image भेजें।",
            reply_markup=back_to_video_tools()
        )
        await query.answer(f"✅ Position {position} selected!")

    elif data == "tool_trim":
        await db.set_video_tool(user_id, "trim")
        await query.message.edit_text(
            "✂️ **Trim Video**\\n\\n"
            "📹 Video file भेजें।\\n"
            "फिर मैं आपसे start time और duration पूछूंगा।",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Trim mode selected! Video भेजें।")

    elif data == "tool_sample":
        await db.set_video_tool(user_id, "sample")
        await query.message.edit_text(
            "🎬 **Sample Video**\\n\\n"
            "📹 Video file भेजें 30-second sample generate करने के लिए।",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ Sample mode selected! Video भेजें।")

    elif data == "tool_mediainfo":
        await db.set_video_tool(user_id, "mediainfo")
        await query.message.edit_text(
            "📊 **MediaInfo**\\n\\n"
            "📹 Video file भेजें detailed information के लिए।",
            reply_markup=back_to_video_tools()
        )
        await query.answer("✅ MediaInfo mode selected! Video भेजें।")
    
