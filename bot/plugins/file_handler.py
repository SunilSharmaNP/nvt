from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.helpers.ffmpeg_helper import FFmpegHelper
from bot.helpers.download_helper import DownloadHelper
from bot.helpers.upload_helper import UploadHelper
from bot.utils.helpers import (
    is_video_file, is_audio_file, is_subtitle_file,
    is_authorized_group, can_use_in_private, format_size
)
from config import Config
import os
import asyncio

@Client.on_message(filters.video | filters.document | filters.audio | filters.photo)
async def handle_file(client: Client, message: Message):
    """Handle incoming video/document/audio/photo files"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    if await db.is_user_banned(user_id):
        return

    if message.chat.type == "private":
        if not await can_use_in_private(user_id):
            await message.reply_text(
                "⚠️ **Private Chat Restricted**\\n\\n"
                "Bot authorized groups में काम करता है।\\n"
                f"Owner: `{Config.OWNER_ID}`"
            )
            return
    else:
        if not await is_authorized_group(chat_id):
            return

        if not await db.is_user_active(user_id, chat_id):
            return

    user = await db.get_user(user_id)
    if not user:
        await db.add_user(user_id, message.from_user.username)
        user = await db.get_user(user_id)

    active_task = await db.get_user_task(user_id)
    if active_task:
        await message.reply_text(
            "⚠️ **Task Already Running**\\n\\n"
            "पहले से ही एक task चल रहा है।\\n"
            "/stop से cancel करें।"
        )
        return

    video_tool = user.get("video_tool_selected")

    if not video_tool:
        await message.reply_text(
            "⚠️ **No Tool Selected**\\n\\n"
            "पहले **Video Tools** menu से tool select करें!\\n"
            "/start उपयोग करें।"
        )
        return

    settings = user.get("settings", Config.DEFAULT_SETTINGS)

    if message.video:
        file_obj = message.video
        file_name = file_obj.file_name or f"video_{user_id}.mp4"
    elif message.document:
        file_obj = message.document
        file_name = file_obj.file_name or f"document_{user_id}"
    elif message.audio:
        file_obj = message.audio
        file_name = file_obj.file_name or f"audio_{user_id}.mp3"
    elif message.photo:
        file_obj = message.photo
        file_name = f"photo_{user_id}.jpg"
    else:
        return

    if file_obj.file_size > Config.MAX_FILE_SIZE:
        await message.reply_text(
            f"❌ **File Too Large**\\n\\n"
            f"Maximum size: {format_size(Config.MAX_FILE_SIZE)}\\n"
            f"Your file: {format_size(file_obj.file_size)}"
        )
        return

    if video_tool == "merge":
        await handle_merge(client, message, user, file_name, file_obj)
    elif video_tool == "encoding":
        await handle_encoding(client, message, user, file_name, file_obj)
    elif video_tool == "convert":
        await handle_convert(client, message, user, file_name, file_obj)
    elif video_tool == "watermark":
        await handle_watermark(client, message, user, file_name, file_obj)
    elif video_tool == "trim":
        await handle_trim(client, message, user, file_name, file_obj)
    elif video_tool == "sample":
        await handle_sample(client, message, user, file_name, file_obj)
    elif video_tool == "mediainfo":
        await handle_mediainfo(client, message, user, file_name, file_obj)

async def handle_merge(client, message, user, file_name, file_obj):
    """Handle video merge"""
    user_id = user["user_id"]
    merge_type = user.get("merge_type")

    if not merge_type:
        await message.reply_text("⚠️ पहले merge type select करें!")
        return

    file_info = {
        "file_id": file_obj.file_id,
        "file_name": file_name,
        "file_type": "video" if is_video_file(file_name) else "audio" if is_audio_file(file_name) else "subtitle" if is_subtitle_file(file_name) else "image",
        "message_id": message.id
    }
    await db.add_temp_file(user_id, file_info)

    temp_files = await db.get_temp_files(user_id)

    if merge_type == "video_video":
        video_count = sum(1 for f in temp_files if f["file_type"] == "video")
        if video_count < 2:
            await message.reply_text(f"✅ Video {video_count}/2 प्राप्त। एक और video भेजें।")
            return
    elif merge_type == "video_audio":
        video_count = sum(1 for f in temp_files if f["file_type"] == "video")
        audio_count = sum(1 for f in temp_files if f["file_type"] == "audio")

        if video_count == 0:
            await message.reply_text("✅ अब video file भेजें।")
            return
        elif audio_count == 0:
            await message.reply_text("✅ Audio प्राप्त। Processing शुरू...")
    elif merge_type == "video_subs":
        video_count = sum(1 for f in temp_files if f["file_type"] == "video")
        sub_count = sum(1 for f in temp_files if f["file_type"] == "subtitle")

        if video_count == 0:
            await message.reply_text("✅ अब video file भेजें।")
            return
        elif sub_count == 0:
            await message.reply_text("✅ Subtitle प्राप्त। Processing शुरू...")

    await process_merge(client, message, user, temp_files, merge_type)

async def process_merge(client, message, user, temp_files, merge_type):
    """Process merge operation"""
    user_id = user["user_id"]
    settings = user.get("settings", Config.DEFAULT_SETTINGS)

    status_msg = await message.reply_text("⏳ **Processing...**\\n\\nDownloading files...")

    try:
        task_id = await db.add_task(user_id, f"merge_{merge_type}")

        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)

        downloaded_files = []
        for idx, file_info in enumerate(temp_files):
            file_path = os.path.join(download_dir, f"{idx}_{file_info['file_name']}")
            
            msg = await client.get_messages(message.chat.id, file_info['message_id'])
            result = await DownloadHelper.download_telegram_file(client, msg, file_path, status_msg)
            
            if result:
                downloaded_files.append({"path": file_path, "type": file_info["file_type"]})

        await status_msg.edit_text("⏳ **Processing...**\\n\\nMerging files...")

        output_file = os.path.join(download_dir, f"merged_{user_id}.mp4")

        if merge_type == "video_video":
            videos = [f["path"] for f in downloaded_files if f["type"] == "video"]
            success = await FFmpegHelper.merge_videos(videos, output_file, status_msg)
        elif merge_type == "video_audio":
            video = next(f["path"] for f in downloaded_files if f["type"] == "video")
            audio = next(f["path"] for f in downloaded_files if f["type"] == "audio")
            success = await FFmpegHelper.merge_video_audio(video, audio, output_file, status_msg)
        else:
            video = next(f["path"] for f in downloaded_files if f["type"] == "video")
            subtitle = next(f["path"] for f in downloaded_files if f["type"] == "subtitle")
            success = await FFmpegHelper.merge_video_subtitle(video, subtitle, output_file, status_msg)

        if not success:
            await status_msg.edit_text("❌ **Merge Failed**\\n\\nProcessing में error आई।")
            await db.complete_task(task_id)
            return

        await status_msg.edit_text("⏳ **Processing...**\\n\\nUploading result...")

        as_document = settings.get("send_as") == "document"
        caption = f"✅ Merged: {merge_type.replace('_', ' + ').title()}"

        if settings.get("upload_mode") == "telegram":
            await UploadHelper.upload_to_telegram(
                client, message.chat.id, output_file,
                caption=caption, as_document=as_document, status_msg=status_msg
            )
            await status_msg.edit_text("✅ **Merge Complete!**")
        else:
            link = await UploadHelper.upload_to_gofile(output_file, status_msg)
            if link:
                await status_msg.edit_text(f"✅ **Merge Complete!**\\n\\n🔗 **Link:**\\n{link}")
            else:
                await status_msg.edit_text("❌ **Upload Failed**")

        await db.clear_temp_files(user_id)
        await db.complete_task(task_id)

        for file in downloaded_files:
            if os.path.exists(file["path"]):
                os.remove(file["path"])
        if os.path.exists(output_file):
            os.remove(output_file)

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await db.clear_temp_files(user_id)

async def handle_encoding(client, message, user, file_name, file_obj):
    """Handle video encoding"""
    if not is_video_file(file_name):
        await message.reply_text("⚠️ Video file भेजें encoding के लिए!")
        return

    user_id = user["user_id"]
    settings = user.get("settings", Config.DEFAULT_SETTINGS)
    encoding_settings = user.get("encoding_settings")

    if not encoding_settings:
        await message.reply_text("⚠️ पहले encoding quality preset select करें!")
        return

    status_msg = await message.reply_text("⏳ **Encoding Video...**\\n\\nDownloading...")

    try:
        task_id = await db.add_task(user_id, "encoding")

        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        input_file = os.path.join(download_dir, file_name)
        output_file = os.path.join(download_dir, f"encoded_{file_name}")

        await DownloadHelper.download_telegram_file(client, message, input_file, status_msg)

        await status_msg.edit_text("⏳ **Encoding Video...**\\n\\nEncoding...")

        success = await FFmpegHelper.encode_video(input_file, output_file, encoding_settings, status_msg)

        if not success:
            await status_msg.edit_text("❌ **Encoding Failed**")
            await db.complete_task(task_id)
            return

        await status_msg.edit_text("⏳ **Encoding Video...**\\n\\nUploading...")

        as_document = settings.get("send_as") == "document"
        quality = encoding_settings.get("preset_name", "custom")
        caption = f"✅ Encoded: {quality.upper()}"

        await UploadHelper.upload_to_telegram(
            client, message.chat.id, output_file,
            caption=caption, as_document=as_document, status_msg=status_msg
        )

        await status_msg.edit_text("✅ **Encoding Complete!**")
        await db.complete_task(task_id)
        await db.set_video_tool(user_id, None)

        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

async def handle_convert(client, message, user, file_name, file_obj):
    """Handle document/video conversion"""
    user_id = user["user_id"]
    settings = user.get("settings", Config.DEFAULT_SETTINGS)
    
    as_document = not (message.document is not None)
    
    status_msg = await message.reply_text("🔄 **Converting...**")
    
    try:
        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        file_path = os.path.join(download_dir, file_name)
        
        await DownloadHelper.download_telegram_file(client, message, file_path, status_msg)
        
        await status_msg.edit_text("🔄 **Converting...**\\n\\nUploading...")
        
        caption = "✅ Converted"
        await UploadHelper.upload_to_telegram(
            client, message.chat.id, file_path,
            caption=caption, as_document=as_document, status_msg=status_msg
        )
        
        await status_msg.edit_text("✅ **Convert Complete!**")
        await db.set_video_tool(user_id, None)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

async def handle_watermark(client, message, user, file_name, file_obj):
    """Handle watermark addition"""
    user_id = user["user_id"]
    
    file_info = {
        "file_id": file_obj.file_id,
        "file_name": file_name,
        "file_type": "video" if is_video_file(file_name) else "image",
        "message_id": message.id
    }
    await db.add_temp_file(user_id, file_info)
    
    temp_files = await db.get_temp_files(user_id)
    video_count = sum(1 for f in temp_files if f["file_type"] == "video")
    image_count = sum(1 for f in temp_files if f["file_type"] == "image")
    
    if video_count == 0:
        await message.reply_text("✅ अब watermark image भेजें।")
        return
    elif image_count == 0:
        await message.reply_text("✅ Watermark image प्राप्त। Processing...")
    
    await process_watermark(client, message, user, temp_files)

async def process_watermark(client, message, user, temp_files):
    """Process watermark addition"""
    user_id = user["user_id"]
    settings = user.get("settings", Config.DEFAULT_SETTINGS)
    position = user.get("watermark_position", "topright")
    
    status_msg = await message.reply_text("⏳ **Adding Watermark...**\\n\\nDownloading...")
    
    try:
        task_id = await db.add_task(user_id, "watermark")
        
        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        
        video_file = None
        watermark_file = None
        
        for file_info in temp_files:
            file_path = os.path.join(download_dir, file_info['file_name'])
            msg = await client.get_messages(message.chat.id, file_info['message_id'])
            await DownloadHelper.download_telegram_file(client, msg, file_path, status_msg)
            
            if file_info["file_type"] == "video":
                video_file = file_path
            else:
                watermark_file = file_path
        
        await status_msg.edit_text("⏳ **Adding Watermark...**\\n\\nProcessing...")
        
        output_file = os.path.join(download_dir, f"watermarked_{user_id}.mp4")
        success = await FFmpegHelper.add_watermark(video_file, watermark_file, output_file, position, status_msg)
        
        if not success:
            await status_msg.edit_text("❌ **Watermark Failed**")
            await db.complete_task(task_id)
            return
        
        await status_msg.edit_text("⏳ **Adding Watermark...**\\n\\nUploading...")
        
        as_document = settings.get("send_as") == "document"
        caption = f"✅ Watermark Added ({position})"
        
        await UploadHelper.upload_to_telegram(
            client, message.chat.id, output_file,
            caption=caption, as_document=as_document, status_msg=status_msg
        )
        
        await status_msg.edit_text("✅ **Watermark Complete!**")
        await db.clear_temp_files(user_id)
        await db.complete_task(task_id)
        
        for path in [video_file, watermark_file, output_file]:
            if path and os.path.exists(path):
                os.remove(path)
                
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await db.clear_temp_files(user_id)

async def handle_trim(client, message, user, file_name, file_obj):
    """Handle video trimming"""
    user_id = user["user_id"]
    await message.reply_text(
        "✂️ **Trim Settings**\\n\\n"
        "अब मुझे बताएं:\\n"
        "Start time (HH:MM:SS format) और Duration (seconds)\\n\\n"
        "Example: `00:00:30 60` (30 seconds से start, 60 seconds duration)"
    )

async def handle_sample(client, message, user, file_name, file_obj):
    """Handle sample generation"""
    user_id = user["user_id"]
    settings = user.get("settings", Config.DEFAULT_SETTINGS)

    if not is_video_file(file_name):
        await message.reply_text("⚠️ Video file भेजें!")
        return

    status_msg = await message.reply_text("🎬 **Generating Sample...**")

    try:
        task_id = await db.add_task(user_id, "sample")

        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        input_file = os.path.join(download_dir, file_name)
        output_file = os.path.join(download_dir, f"sample_{file_name}")

        await DownloadHelper.download_telegram_file(client, message, input_file, status_msg)
        await status_msg.edit_text("🎬 **Generating Sample...**\\n\\nProcessing...")

        success = await FFmpegHelper.generate_sample(input_file, output_file, duration=30, status_msg=status_msg)

        if success:
            await client.send_video(
                message.chat.id,
                output_file,
                caption="✅ 30-second sample generated"
            )
            await status_msg.edit_text("✅ **Sample Generated!**")
        else:
            await status_msg.edit_text("❌ **Sample Generation Failed**")

        await db.complete_task(task_id)
        await db.set_video_tool(user_id, None)

        for path in [input_file, output_file]:
            if os.path.exists(path):
                os.remove(path)

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

async def handle_mediainfo(client, message, user, file_name, file_obj):
    """Handle mediainfo extraction"""
    user_id = user["user_id"]

    if not is_video_file(file_name):
        await message.reply_text("⚠️ Video file भेजें!")
        return

    status_msg = await message.reply_text("📊 **Extracting MediaInfo...**")

    try:
        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        input_file = os.path.join(download_dir, file_name)

        await DownloadHelper.download_telegram_file(client, message, input_file, status_msg)

        media_info = await FFmpegHelper.get_mediainfo_text(input_file)

        await status_msg.edit_text(media_info)
        await db.set_video_tool(user_id, None)

        if os.path.exists(input_file):
            os.remove(input_file)

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
  
