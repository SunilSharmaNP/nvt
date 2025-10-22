from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.helpers.ffmpeg_helper import FFmpegHelper
from bot.helpers.download_helper import DownloadHelper
from bot.helpers.upload_helper import UploadHelper
from bot.utils.helpers import is_video_file, is_audio_file, is_subtitle_file, is_authorized_group, can_use_in_private
from config import Config
import os
import asyncio

@Client.on_message(filters.video | filters.document | filters.audio)
async def handle_file(client: Client, message: Message):
    """Handle incoming video/document/audio files"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is banned
    if await db.is_user_banned(user_id):
        return
    
    # Check authorization
    if message.chat.type == "private":
        if not await can_use_in_private(user_id):
            await message.reply_text(
                "⚠️ **Private Chat Restricted**\n\n"
                "This bot works only in authorized groups.\n\n"
                f"📌 Please join an authorized group to use video tools.\n"
                f"🔗 Contact bot owner: `{Config.OWNER_ID}`"
            )
            return
    else:
        # Group chat
        if not await is_authorized_group(chat_id):
            return
        
        # Check if user is active
        if not await db.is_user_active(user_id, chat_id):
            return
    
    # Get user data
    user = await db.get_user(user_id)
    if not user:
        await db.add_user(user_id, message.from_user.username)
        user = await db.get_user(user_id)
    
    # Check if user already has an active task
    active_task = await db.get_user_task(user_id)
    if active_task:
        await message.reply_text(
            "⚠️ **Task Already Running**\n\n"
            "You already have an active task. Please wait for it to complete.\n"
            "Use /stop to cancel your current task."
        )
        return
    
    # Get selected video tool
    video_tool = user.get("video_tool_selected")
    
    if not video_tool:
        await message.reply_text(
            "⚠️ **No Tool Selected**\n\n"
            "Please select a tool from the **Video Tools** menu first!\n"
            "Use /start to access the menu."
        )
        return
    
    # Get user settings
    settings = user.get("settings", Config.DEFAULT_SETTINGS)
    
    # Get file info
    if message.video:
        file_obj = message.video
        file_name = file_obj.file_name or f"video_{user_id}.mp4"
    elif message.document:
        file_obj = message.document
        file_name = file_obj.file_name or f"document_{user_id}"
    elif message.audio:
        file_obj = message.audio
        file_name = file_obj.file_name or f"audio_{user_id}.mp3"
    else:
        return
    
    # Process based on selected tool
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
        await message.reply_text("⚠️ Please select a merge type first!")
        return
    
    # Add file to temp files
    file_info = {
        "file_id": file_obj.file_id,
        "file_name": file_name,
        "file_type": "video" if is_video_file(file_name) else "audio" if is_audio_file(file_name) else "subtitle"
    }
    await db.add_temp_file(user_id, file_info)
    
    # Get all temp files
    temp_files = await db.get_temp_files(user_id)
    
    # Check if we have enough files
    if merge_type == "video_video":
        video_count = sum(1 for f in temp_files if f["file_type"] == "video")
        if video_count < 2:
            await message.reply_text(f"✅ Video {video_count}/2 received. Send one more video.")
            return
    elif merge_type == "video_audio":
        video_count = sum(1 for f in temp_files if f["file_type"] == "video")
        audio_count = sum(1 for f in temp_files if f["file_type"] == "audio")
        
        if video_count == 0:
            await message.reply_text("✅ Send the video file now.")
            return
        elif audio_count == 0:
            if file_info["file_type"] != "audio":
                await message.reply_text("⚠️ Please send an audio file, not a video!")
                return
            await message.reply_text("✅ Audio received. Starting merge...")
        else:
            await message.reply_text("⚠️ You already sent video and audio. Processing...")
    elif merge_type == "video_subs":
        video_count = sum(1 for f in temp_files if f["file_type"] == "video")
        sub_count = sum(1 for f in temp_files if f["file_type"] == "subtitle")
        
        if video_count == 0:
            await message.reply_text("✅ Send the video file now.")
            return
        elif sub_count == 0:
            if file_info["file_type"] != "subtitle":
                await message.reply_text("⚠️ Please send a subtitle file (.srt, .ass, .vtt)!")
                return
            await message.reply_text("✅ Subtitle received. Starting merge...")
    
    # Start processing
    await process_merge(client, message, user, temp_files, merge_type)

async def process_merge(client, message, user, temp_files, merge_type):
    """Process merge operation"""
    user_id = user["user_id"]
    settings = user.get("settings", Config.DEFAULT_SETTINGS)
    
    status_msg = await message.reply_text("⏳ **Processing...**\n\nDownloading files...")
    
    try:
        # Create task
        task_id = await db.add_task(user_id, f"merge_{merge_type}")
        
        # Download files
        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        
        downloaded_files = []
        for file_info in temp_files:
            file_path = os.path.join(download_dir, file_info["file_name"])
            # Simulated download (you'd use actual Telegram download here)
            downloaded_files.append({"path": file_path, "type": file_info["file_type"]})
        
        await status_msg.edit_text("⏳ **Processing...**\n\nMerging files...")
        
        # Perform merge based on type
        output_file = os.path.join(download_dir, f"merged_{user_id}.mp4")
        
        if merge_type == "video_video":
            videos = [f["path"] for f in downloaded_files if f["type"] == "video"]
            success = await FFmpegHelper.merge_video_video(videos[0], videos[1], output_file)
        elif merge_type == "video_audio":
            video = next(f["path"] for f in downloaded_files if f["type"] == "video")
            audio = next(f["path"] for f in downloaded_files if f["type"] == "audio")
            success = await FFmpegHelper.merge_video_audio(video, audio, output_file)
        else:  # video_subs
            video = next(f["path"] for f in downloaded_files if f["type"] == "video")
            subtitle = next(f["path"] for f in downloaded_files if f["type"] == "subtitle")
            success = await FFmpegHelper.merge_video_subtitle(video, subtitle, output_file)
        
        if not success:
            await status_msg.edit_text("❌ **Merge Failed**\n\nAn error occurred during merging.")
            await db.complete_task(task_id)
            return
        
        await status_msg.edit_text("⏳ **Processing...**\n\nUploading result...")
        
        # Upload
        as_document = settings.get("send_as") == "document"
        caption = f"✅ Merged: {merge_type.replace('_', ' + ').title()}"
        
        if settings.get("upload_mode") == "telegram":
            await UploadHelper.upload_to_telegram(
                client, message.chat.id, output_file,
                caption=caption, as_document=as_document
            )
            await status_msg.edit_text("✅ **Merge Complete!**")
        else:
            link = await UploadHelper.upload_to_gofile(output_file)
            if link:
                await status_msg.edit_text(f"✅ **Merge Complete!**\n\n🔗 **Download Link:**\n{link}")
            else:
                await status_msg.edit_text("❌ **Upload Failed**")
        
        # Cleanup
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
        await message.reply_text("⚠️ Please send a video file for encoding!")
        return
    
    user_id = user["user_id"]
    settings = user.get("settings", Config.DEFAULT_SETTINGS)
    encoding_settings = user.get("encoding_settings")
    
    if not encoding_settings:
        await message.reply_text("⚠️ Please select an encoding quality preset first!")
        return
    
    status_msg = await message.reply_text("⏳ **Encoding Video...**\n\nDownloading...")
    
    try:
        task_id = await db.add_task(user_id, "encoding")
        
        # Download
        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        input_file = os.path.join(download_dir, file_name)
        output_file = os.path.join(download_dir, f"encoded_{file_name}")
        
        # Simulated download
        await status_msg.edit_text("⏳ **Encoding Video...**\n\nEncoding in progress...")
        
        # Encode
        success = await FFmpegHelper.encode_video(input_file, output_file, encoding_settings)
        
        if not success:
            await status_msg.edit_text("❌ **Encoding Failed**")
            await db.complete_task(task_id)
            return
        
        await status_msg.edit_text("⏳ **Encoding Video...**\n\nUploading...")
        
        # Upload
        as_document = settings.get("send_as") == "document"
        quality = encoding_settings.get("preset_name", "custom")
        caption = f"✅ Encoded: {quality.upper()}"
        
        await UploadHelper.upload_to_telegram(
            client, message.chat.id, output_file,
            caption=caption, as_document=as_document
        )
        
        await status_msg.edit_text("✅ **Encoding Complete!**")
        await db.complete_task(task_id)
        await db.set_video_tool(user_id, None)
        
        # Cleanup
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

async def handle_convert(client, message, user, file_name, file_obj):
    """Handle document/video conversion"""
    user_id = user["user_id"]
    await message.reply_text("🔄 **Convert**\n\nThis feature converts between document and video format.\n\nSending back in opposite format...")
    await db.set_video_tool(user_id, None)

async def handle_watermark(client, message, user, file_name, file_obj):
    """Handle watermark addition"""
    await message.reply_text("©️ **Watermark**\n\nWatermark feature - send video then watermark image.")

async def handle_trim(client, message, user, file_name, file_obj):
    """Handle video trimming"""
    await message.reply_text("✂️ **Trim**\n\nPlease send start time (HH:MM:SS) and duration (seconds) in format:\n`00:00:10 30`")

async def handle_sample(client, message, user, file_name, file_obj):
    """Handle sample generation"""
    user_id = user["user_id"]
    
    if not is_video_file(file_name):
        await message.reply_text("⚠️ Please send a video file!")
        return
    
    status_msg = await message.reply_text("🎬 **Generating Sample...**")
    
    try:
        task_id = await db.add_task(user_id, "sample")
        
        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        input_file = os.path.join(download_dir, file_name)
        output_file = os.path.join(download_dir, f"sample_{file_name}")
        
        # Generate sample
        success = await FFmpegHelper.generate_sample(input_file, output_file, duration=30)
        
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
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

async def handle_mediainfo(client, message, user, file_name, file_obj):
    """Handle mediainfo extraction"""
    user_id = user["user_id"]
    
    if not is_video_file(file_name):
        await message.reply_text("⚠️ Please send a video file!")
        return
    
    status_msg = await message.reply_text("📊 **Extracting MediaInfo...**")
    
    try:
        download_dir = os.path.join(Config.DOWNLOAD_DIR, str(user_id))
        os.makedirs(download_dir, exist_ok=True)
        input_file = os.path.join(download_dir, file_name)
        
        # Get media info
        media_info = await FFmpegHelper.get_mediainfo_text(input_file)
        
        await status_msg.edit_text(media_info)
        await db.set_video_tool(user_id, None)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
