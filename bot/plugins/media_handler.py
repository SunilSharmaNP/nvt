import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from bot.helpers import FFmpegHelper, DownloadHelper, UploadHelper
from bot.helpers.buttons import cancel_process_buttons, back_to_main, back_to_video_tools
from bot.utils.helpers import (
    is_video_file, is_audio_file, is_subtitle_file, is_image_file,
    format_size, is_authorized_group
)
from config import Config

async def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except:
            pass

@Client.on_message(filters.video | filters.document | filters.audio | filters.photo)
async def handle_media(client: Client, message: Message):
    """Handle all incoming media files"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is banned
    if await db.is_user_banned(user_id):
        await message.reply_text("❌ You are banned from using this bot.")
        return
    
    # Check group authorization
    if message.chat.type != "private":
        if not await is_authorized_group(chat_id):
            return
        
        if not await db.is_user_active(user_id, chat_id):
            await message.reply_text(
                "⚠️ **Bot Not Activated**\n\n"
                f"Use /start to activate the bot, {message.from_user.mention}!"
            )
            return
    
    # Check if user has an active task
    active_task = await db.get_user_task(user_id)
    if active_task:
        await message.reply_text(
            "⚠️ **Task Already Running**\n\n"
            "You have an active task. Please wait for it to complete or use /stop to cancel it."
        )
        return
    
    # Get user data
    user = await db.get_user(user_id)
    if not user:
        await db.add_user(user_id, message.from_user.username)
        user = await db.get_user(user_id)
    
    selected_tool = user.get("video_tool_selected")
    
    if not selected_tool:
        await message.reply_text(
            "⚠️ **No Tool Selected**\n\n"
            "Please select a tool from the Video Tools menu first!"
        )
        return
    
    # Handle based on selected tool
    if selected_tool == "encoding":
        await handle_encoding(client, message, user)
    elif selected_tool == "merge":
        await handle_merge(client, message, user)
    elif selected_tool == "mediainfo":
        await handle_mediainfo(client, message, user)
    elif selected_tool == "sample":
        await handle_sample(client, message, user)
    elif selected_tool == "watermark":
        await handle_watermark(client, message, user)
    elif selected_tool == "trim":
        # Check if trim settings are already set
        trim_settings = user.get("trim_settings")
        if trim_settings:
            await handle_trim(client, message, user, trim_settings)
        else:
            # Store video for later trimming
            if message.video:
                file_obj = message.video
            elif message.document and is_video_file(message.document.file_name):
                file_obj = message.document
            else:
                await message.reply_text("❌ Please send a video file!")
                return
            
            file_info = {
                "type": "video",
                "file_id": file_obj.file_id,
                "file_name": getattr(file_obj, "file_name", "video_file"),
                "file_size": file_obj.file_size,
                "message_id": message.id,
                "chat_id": message.chat.id
            }
            
            await db.add_temp_file(user_id, file_info)
            
            await message.reply_text(
                "✂️ **Trim Mode Active**\n\n"
                "📹 Video received! Now send trim times.\n\n"
                "**Format:** `start:end` (in seconds)\n"
                "**Example:** `10:120`"
            )
    else:
        await message.reply_text(f"⚠️ Tool '{selected_tool}' is not yet implemented.")

async def handle_encoding(client: Client, message: Message, user: dict):
    """Handle video encoding"""
    user_id = message.from_user.id
    
    encoding_settings = user.get("encoding_settings")
    if not encoding_settings:
        await message.reply_text(
            "⚠️ **No Quality Selected**\n\n"
            "Please select a quality preset from the encoding menu first!"
        )
        return
    
    # Check if it's a video
    if message.video:
        file_obj = message.video
    elif message.document and is_video_file(message.document.file_name):
        file_obj = message.document
    else:
        await message.reply_text("❌ Please send a video file!")
        return
    
    # Create task
    task_id = await db.add_task(user_id, "encoding", "processing")
    
    status_msg = await message.reply_text(
        "⏬ **Starting Download...**\n\n"
        f"📁 File: `{file_obj.file_name or 'video'}`\n"
        f"📦 Size: `{format_size(file_obj.file_size)}`",
        reply_markup=cancel_process_buttons()
    )
    
    input_file = None
    output_file = None
    
    try:
        # Download
        input_file = os.path.join(
            Config.DOWNLOAD_DIR,
            f"{user_id}_input_{file_obj.file_unique_id}.{file_obj.file_name.split('.')[-1] if file_obj.file_name else 'mp4'}"
        )
        
        downloaded = await DownloadHelper.download_telegram_file(
            client, message, input_file, status_msg
        )
        
        if not downloaded:
            await status_msg.edit_text("❌ Download failed!")
            await db.complete_task(task_id)
            return
        
        # Encode
        preset_name = encoding_settings.get("preset_name", "720p")
        output_file = os.path.join(
            Config.DOWNLOAD_DIR,
            f"{user_id}_encoded_{preset_name}_{file_obj.file_unique_id}.mp4"
        )
        
        await status_msg.edit_text(
            f"⚙️ **Encoding to {preset_name.upper()}...**\n\n"
            "Please wait, this may take a while..."
        )
        
        success = await FFmpegHelper.encode_video(
            input_file, output_file, encoding_settings, status_msg
        )
        
        if not success or not os.path.exists(output_file):
            await status_msg.edit_text("❌ Encoding failed!")
            await cleanup_files(input_file, output_file)
            await db.complete_task(task_id)
            return
        
        # Upload
        settings = user.get("settings", Config.DEFAULT_SETTINGS)
        upload_mode = settings.get("upload_mode", "telegram")
        
        if upload_mode == "telegram":
            await status_msg.edit_text("⏫ **Uploading to Telegram...**")
            
            caption = f"🎬 Encoded to {preset_name.upper()}\n\n"
            caption += f"📦 Size: {format_size(os.path.getsize(output_file))}\n"
            caption += f"⚙️ Codec: {encoding_settings.get('codec', 'libx264')}"
            
            await UploadHelper.upload_to_telegram(
                client,
                message.chat.id,
                output_file,
                caption=caption,
                as_document=(settings.get("send_as") == "document"),
                status_msg=status_msg
            )
            
            await status_msg.delete()
            
        elif upload_mode == "gofile":
            await status_msg.edit_text("⏫ **Uploading to GoFile...**")
            
            gofile_link = await UploadHelper.upload_to_gofile(output_file, status_msg)
            
            if gofile_link:
                await message.reply_text(
                    f"✅ **Upload Complete!**\n\n"
                    f"🔗 **GoFile Link:**\n{gofile_link}\n\n"
                    f"📦 Size: {format_size(os.path.getsize(output_file))}"
                )
            else:
                await status_msg.edit_text("❌ GoFile upload failed!")
            
            await status_msg.delete()
        
        # Cleanup
        await cleanup_files(input_file, output_file)
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)
        
    except Exception as e:
        print(f"Encoding error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await cleanup_files(input_file, output_file)
        await db.complete_task(task_id)

async def handle_merge(client: Client, message: Message, user: dict):
    """Handle video merging"""
    user_id = message.from_user.id
    merge_type = user.get("merge_type")
    
    if not merge_type:
        await message.reply_text("⚠️ Please select a merge type first!")
        return
    
    # Determine file type
    if message.video or (message.document and is_video_file(message.document.file_name)):
        file_type = "video"
        file_obj = message.video or message.document
    elif message.audio or (message.document and is_audio_file(message.document.file_name)):
        file_type = "audio"
        file_obj = message.audio or message.document
    elif message.document and is_subtitle_file(message.document.file_name):
        file_type = "subtitle"
        file_obj = message.document
    else:
        await message.reply_text("❌ Unsupported file type!")
        return
    
    # Add to merge queue
    temp_files = user.get("temp_files", [])
    
    file_info = {
        "type": file_type,
        "file_id": file_obj.file_id,
        "file_name": getattr(file_obj, "file_name", f"{file_type}_file"),
        "file_size": file_obj.file_size,
        "message_id": message.id,
        "chat_id": message.chat.id
    }
    
    await db.add_temp_file(user_id, file_info)
    temp_files.append(file_info)
    
    # Check if we have required files
    if merge_type == "video_video":
        video_count = sum(1 for f in temp_files if f["type"] == "video")
        if video_count < 2:
            await message.reply_text(
                f"✅ **File {video_count} Added**\n\n"
                f"📹 Send {2 - video_count} more video(s) to merge."
            )
            return
    
    elif merge_type == "video_audio":
        has_video = any(f["type"] == "video" for f in temp_files)
        has_audio = any(f["type"] == "audio" for f in temp_files)
        
        if not has_video:
            await message.reply_text("✅ **Audio Added**\n\n📹 Now send the video file.")
            return
        if not has_audio:
            await message.reply_text("✅ **Video Added**\n\n🎵 Now send the audio file.")
            return
    
    elif merge_type == "video_subs":
        has_video = any(f["type"] == "video" for f in temp_files)
        has_subs = any(f["type"] == "subtitle" for f in temp_files)
        
        if not has_video:
            await message.reply_text("✅ **Subtitle Added**\n\n📹 Now send the video file.")
            return
        if not has_subs:
            await message.reply_text("✅ **Video Added**\n\n💬 Now send the subtitle file.")
            return
    
    # All files received, start merging
    await process_merge(client, message, user, temp_files, merge_type)

async def process_merge(client: Client, message: Message, user: dict, temp_files: list, merge_type: str):
    """Process the merge operation"""
    user_id = message.from_user.id
    task_id = await db.add_task(user_id, f"merge_{merge_type}", "processing")
    
    status_msg = await message.reply_text(
        "⏬ **Downloading Files...**",
        reply_markup=cancel_process_buttons()
    )
    
    downloaded_files = []
    output_file = None
    
    try:
        # Download all files
        for i, file_info in enumerate(temp_files, 1):
            ext = file_info["file_name"].split(".")[-1] if "." in file_info["file_name"] else "mp4"
            local_path = os.path.join(
                Config.DOWNLOAD_DIR,
                f"{user_id}_{file_info['type']}_{i}.{ext}"
            )
            
            # Get the original message using stored message_id and chat_id
            try:
                original_msg = await client.get_messages(
                    file_info["chat_id"],
                    file_info["message_id"]
                )
                
                downloaded = await DownloadHelper.download_telegram_file(
                    client, original_msg, local_path, None
                )
                
                if downloaded:
                    downloaded_files.append({
                        "path": local_path,
                        "type": file_info["type"]
                    })
            except Exception as e:
                print(f"Error downloading file {i}: {e}")
                continue
        
        if not downloaded_files:
            await status_msg.edit_text("❌ Download failed!")
            await cleanup_files(*[f["path"] for f in downloaded_files if "path" in f])
            await db.complete_task(task_id)
            await db.clear_temp_files(user_id)
            return
        
        # Merge based on type
        output_file = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_merged_{merge_type}.mp4")
        
        await status_msg.edit_text(f"🔗 **Merging Files...**\n\nPlease wait...")
        
        success = False
        
        if merge_type == "video_video":
            video_paths = [f["path"] for f in downloaded_files if f["type"] == "video"]
            success = await FFmpegHelper.merge_videos(video_paths, output_file, status_msg)
        
        elif merge_type == "video_audio":
            video_path = next(f["path"] for f in downloaded_files if f["type"] == "video")
            audio_path = next(f["path"] for f in downloaded_files if f["type"] == "audio")
            success = await FFmpegHelper.merge_video_audio(video_path, audio_path, output_file, status_msg)
        
        elif merge_type == "video_subs":
            video_path = next(f["path"] for f in downloaded_files if f["type"] == "video")
            subs_path = next(f["path"] for f in downloaded_files if f["type"] == "subtitle")
            success = await FFmpegHelper.merge_video_subtitle(video_path, subs_path, output_file, status_msg)
        
        if not success or not os.path.exists(output_file):
            await status_msg.edit_text("❌ Merge failed!")
            await cleanup_files(output_file, *[f["path"] for f in downloaded_files])
            await db.complete_task(task_id)
            await db.clear_temp_files(user_id)
            return
        
        # Upload
        settings = user.get("settings", Config.DEFAULT_SETTINGS)
        
        await status_msg.edit_text("⏫ **Uploading...**")
        
        caption = f"🔗 Merged: {merge_type.replace('_', ' + ').title()}\n"
        caption += f"📦 Size: {format_size(os.path.getsize(output_file))}"
        
        await UploadHelper.upload_to_telegram(
            client,
            message.chat.id,
            output_file,
            caption=caption,
            as_document=(settings.get("send_as") == "document"),
            status_msg=status_msg
        )
        
        await status_msg.delete()
        
        # Cleanup
        await cleanup_files(output_file, *[f["path"] for f in downloaded_files])
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)
        
    except Exception as e:
        print(f"Merge error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await cleanup_files(output_file, *[f["path"] for f in downloaded_files])
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)

async def handle_mediainfo(client: Client, message: Message, user: dict):
    """Handle MediaInfo extraction"""
    user_id = message.from_user.id
    
    if message.video:
        file_obj = message.video
    elif message.document and is_video_file(message.document.file_name):
        file_obj = message.document
    else:
        await message.reply_text("❌ Please send a video file!")
        return
    
    task_id = await db.add_task(user_id, "mediainfo", "processing")
    
    status_msg = await message.reply_text("⏬ **Downloading for analysis...**")
    
    input_file = None
    
    try:
        input_file = os.path.join(
            Config.DOWNLOAD_DIR,
            f"{user_id}_mediainfo_{file_obj.file_unique_id}.{file_obj.file_name.split('.')[-1] if file_obj.file_name else 'mp4'}"
        )
        
        downloaded = await DownloadHelper.download_telegram_file(
            client, message, input_file, status_msg
        )
        
        if not downloaded:
            await status_msg.edit_text("❌ Download failed!")
            await db.complete_task(task_id)
            return
        
        await status_msg.edit_text("📊 **Analyzing Media...**")
        
        mediainfo = await FFmpegHelper.get_mediainfo_text(input_file)
        
        await message.reply_text(mediainfo, reply_markup=back_to_video_tools())
        await status_msg.delete()
        
        await cleanup_files(input_file)
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)
        
    except Exception as e:
        print(f"MediaInfo error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await cleanup_files(input_file)
        await db.complete_task(task_id)

async def handle_sample(client: Client, message: Message, user: dict):
    """Handle sample video generation"""
    user_id = message.from_user.id
    
    if message.video:
        file_obj = message.video
    elif message.document and is_video_file(message.document.file_name):
        file_obj = message.document
    else:
        await message.reply_text("❌ Please send a video file!")
        return
    
    # Get sample duration
    sample_duration_key = user.get("sample_duration", "30s")
    sample_duration = Config.SAMPLE_DURATIONS.get(sample_duration_key, 30)
    
    task_id = await db.add_task(user_id, "sample", "processing")
    
    status_msg = await message.reply_text("⏬ **Downloading...**")
    
    input_file = None
    output_file = None
    
    try:
        input_file = os.path.join(
            Config.DOWNLOAD_DIR,
            f"{user_id}_sample_input_{file_obj.file_unique_id}.{file_obj.file_name.split('.')[-1] if file_obj.file_name else 'mp4'}"
        )
        
        downloaded = await DownloadHelper.download_telegram_file(
            client, message, input_file, status_msg
        )
        
        if not downloaded:
            await status_msg.edit_text("❌ Download failed!")
            await db.complete_task(task_id)
            return
        
        # Generate sample
        output_file = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_sample_{sample_duration}s.mp4")
        
        await status_msg.edit_text(f"🎬 **Generating {sample_duration}s sample...**")
        
        success = await FFmpegHelper.generate_sample(input_file, output_file, sample_duration, status_msg)
        
        if not success or not os.path.exists(output_file):
            await status_msg.edit_text("❌ Sample generation failed!")
            await cleanup_files(input_file, output_file)
            await db.complete_task(task_id)
            return
        
        # Upload
        settings = user.get("settings", Config.DEFAULT_SETTINGS)
        
        await status_msg.edit_text("⏫ **Uploading...**")
        
        caption = f"🎬 Sample Video ({sample_duration}s)\n"
        caption += f"📦 Size: {format_size(os.path.getsize(output_file))}"
        
        await UploadHelper.upload_to_telegram(
            client,
            message.chat.id,
            output_file,
            caption=caption,
            as_document=(settings.get("send_as") == "document"),
            status_msg=status_msg
        )
        
        await status_msg.delete()
        
        await cleanup_files(input_file, output_file)
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)
        
    except Exception as e:
        print(f"Sample error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await cleanup_files(input_file, output_file)
        await db.complete_task(task_id)

async def handle_trim(client: Client, message: Message, user: dict, trim_settings: dict):
    """Handle video trimming"""
    user_id = message.from_user.id
    
    if message.video:
        file_obj = message.video
    elif message.document and is_video_file(message.document.file_name):
        file_obj = message.document
    else:
        await message.reply_text("❌ Please send a video file!")
        return
    
    start_time = str(trim_settings.get("start", 0))
    end_time = trim_settings.get("end", 0)
    duration = str(trim_settings.get("duration", 30))
    
    task_id = await db.add_task(user_id, "trim", "processing")
    
    status_msg = await message.reply_text("⏬ **Downloading...**")
    
    input_file = None
    output_file = None
    
    try:
        input_file = os.path.join(
            Config.DOWNLOAD_DIR,
            f"{user_id}_trim_input_{file_obj.file_unique_id}.{file_obj.file_name.split('.')[-1] if file_obj.file_name else 'mp4'}"
        )
        
        downloaded = await DownloadHelper.download_telegram_file(
            client, message, input_file, status_msg
        )
        
        if not downloaded:
            await status_msg.edit_text("❌ Download failed!")
            await db.complete_task(task_id)
            return
        
        # Trim video
        output_file = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_trimmed.mp4")
        
        await status_msg.edit_text(f"✂️ **Trimming video ({start_time}s to {end_time}s)...**")
        
        success = await FFmpegHelper.trim_video(input_file, output_file, start_time, duration, status_msg)
        
        if not success or not os.path.exists(output_file):
            await status_msg.edit_text("❌ Trim failed!")
            await cleanup_files(input_file, output_file)
            await db.complete_task(task_id)
            return
        
        # Upload
        settings = user.get("settings", Config.DEFAULT_SETTINGS)
        
        await status_msg.edit_text("⏫ **Uploading...**")
        
        caption = f"✂️ Trimmed Video\n"
        caption += f"⏱️ {start_time}s to {end_time}s ({duration}s)\n"
        caption += f"📦 Size: {format_size(os.path.getsize(output_file))}"
        
        await UploadHelper.upload_to_telegram(
            client,
            message.chat.id,
            output_file,
            caption=caption,
            as_document=(settings.get("send_as") == "document"),
            status_msg=status_msg
        )
        
        await status_msg.delete()
        
        await cleanup_files(input_file, output_file)
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)
        
    except Exception as e:
        print(f"Trim error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await cleanup_files(input_file, output_file)
        await db.complete_task(task_id)

async def handle_watermark(client: Client, message: Message, user: dict):
    """Handle watermark addition"""
    user_id = message.from_user.id
    
    # Check what we have in temp files
    temp_files = user.get("temp_files", [])
    
    # Determine if this is video or watermark image
    if message.photo or (message.document and is_image_file(message.document.file_name)):
        file_type = "watermark"
        file_obj = message.photo or message.document
    elif message.video or (message.document and is_video_file(message.document.file_name)):
        file_type = "video"
        file_obj = message.video or message.document
    else:
        await message.reply_text("❌ Please send a video file or watermark image!")
        return
    
    # Add to temp files
    file_info = {
        "type": file_type,
        "file_id": file_obj.file_id,
        "file_name": getattr(file_obj, "file_name", f"{file_type}_file"),
        "file_size": getattr(file_obj, "file_size", 0),
        "message_id": message.id,
        "chat_id": message.chat.id
    }
    
    await db.add_temp_file(user_id, file_info)
    temp_files.append(file_info)
    
    # Check if we have both video and watermark
    has_video = any(f["type"] == "video" for f in temp_files)
    has_watermark = any(f["type"] == "watermark" for f in temp_files)
    
    if not has_video:
        await message.reply_text("✅ **Watermark Added**\n\n📹 Now send the video file.")
        return
    if not has_watermark:
        await message.reply_text("✅ **Video Added**\n\n📄 Now send the watermark image.")
        return
    
    # Both files received, start watermarking
    task_id = await db.add_task(user_id, "watermark", "processing")
    status_msg = await message.reply_text("⏬ **Downloading files...**")
    
    video_file = None
    watermark_file = None
    output_file = None
    
    try:
        # Download video
        video_info = next(f for f in temp_files if f["type"] == "video")
        video_file = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_wm_video.mp4")
        
        video_msg = await client.get_messages(video_info["chat_id"], video_info["message_id"])
        await DownloadHelper.download_telegram_file(client, video_msg, video_file, None)
        
        # Download watermark
        watermark_info = next(f for f in temp_files if f["type"] == "watermark")
        watermark_file = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_watermark.png")
        
        wm_msg = await client.get_messages(watermark_info["chat_id"], watermark_info["message_id"])
        await DownloadHelper.download_telegram_file(client, wm_msg, watermark_file, None)
        
        # Get watermark position
        position = user.get("watermark_position", "topright")
        
        # Add watermark
        output_file = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_watermarked.mp4")
        
        await status_msg.edit_text(f"©️ **Adding watermark ({position})...**")
        
        success = await FFmpegHelper.add_watermark(video_file, watermark_file, output_file, position, status_msg)
        
        if not success or not os.path.exists(output_file):
            await status_msg.edit_text("❌ Watermark addition failed!")
            await cleanup_files(video_file, watermark_file, output_file)
            await db.complete_task(task_id)
            await db.clear_temp_files(user_id)
            return
        
        # Upload
        settings = user.get("settings", Config.DEFAULT_SETTINGS)
        
        await status_msg.edit_text("⏫ **Uploading...**")
        
        caption = f"©️ Watermarked ({position.title()})\n"
        caption += f"📦 Size: {format_size(os.path.getsize(output_file))}"
        
        await UploadHelper.upload_to_telegram(
            client,
            message.chat.id,
            output_file,
            caption=caption,
            as_document=(settings.get("send_as") == "document"),
            status_msg=status_msg
        )
        
        await status_msg.delete()
        
        await cleanup_files(video_file, watermark_file, output_file)
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)
        
    except Exception as e:
        print(f"Watermark error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        await cleanup_files(video_file, watermark_file, output_file)
        await db.complete_task(task_id)
        await db.clear_temp_files(user_id)
