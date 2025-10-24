import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database import db
from config import Config

@Client.on_message(filters.photo & filters.private)
async def handle_thumbnail_photo(client: Client, message: Message):
    """Handle thumbnail photo upload"""
    user_id = message.from_user.id
    
    # Check if user is banned
    if await db.is_user_banned(user_id):
        return
    
    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await db.add_user(user_id, message.from_user.username)
        user = await db.get_user(user_id)
    
    # Download thumbnail
    thumbnail_path = os.path.join(
        Config.DOWNLOAD_DIR,
        f"thumb_{user_id}_{int(time.time())}.jpg"
    )
    
    try:
        await message.download(file_name=thumbnail_path)
        
        # Save thumbnail path to user settings
        await db.update_user_setting(user_id, "thumbnail", thumbnail_path)
        
        await message.reply_text(
            "✅ **Thumbnail Set Successfully!**\n\n"
            "🖼️ This thumbnail will be used for all future uploads.\n"
            "❌ Send /clearthumb to remove it."
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error saving thumbnail:** {str(e)}")

@Client.on_message(filters.text & ~filters.command(["start", "stop", "help", "s"]))
async def handle_text_input(client: Client, message: Message):
    """Handle text inputs for filename and trim settings"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip()
    
    # Check if user is banned
    if await db.is_user_banned(user_id):
        return
    
    # For group messages, check authorization
    if message.chat.type != "private":
        from bot.utils.helpers import is_authorized_group
        if not await is_authorized_group(chat_id):
            return
    
    # Get user data
    user = await db.get_user(user_id)
    if not user:
        await db.add_user(user_id, message.from_user.username)
        user = await db.get_user(user_id)
    
    selected_tool = user.get("video_tool_selected")
    
    # Check if this is a trim command (format: start:end)
    if selected_tool == "trim" and ":" in text:
        await handle_trim_input(client, message, user, text)
        return
    
    # Otherwise, treat as filename input (only in private chats to avoid spam)
    if message.chat.type == "private":
        await handle_filename_input(client, message, text)

async def handle_filename_input(client: Client, message: Message, filename: str):
    """Handle filename customization"""
    user_id = message.from_user.id
    
    try:
        # Validate filename (basic check)
        if len(filename) > 100:
            await message.reply_text("❌ Filename too long! Maximum 100 characters.")
            return
        
        # Save filename pattern
        await db.update_user_setting(user_id, "filename", filename)
        
        await message.reply_text(
            f"✅ **Filename Pattern Updated!**\n\n"
            f"📝 New pattern: `{filename}`\n\n"
            f"Variables:\n"
            f"• `{{original}}` = Original filename\n"
            f"• `{{time}}` = Timestamp\n\n"
            f"Send /defaultname to reset to default."
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")

async def handle_trim_input(client: Client, message: Message, user: dict, trim_text: str):
    """Handle trim time input"""
    user_id = message.from_user.id
    
    try:
        # Parse trim times
        if ":" not in trim_text:
            await message.reply_text(
                "❌ **Invalid format!**\n\n"
                "Use: `start:end` (in seconds)\n"
                "Example: `10:120`"
            )
            return
        
        parts = trim_text.split(":")
        if len(parts) != 2:
            await message.reply_text(
                "❌ **Invalid format!**\n\n"
                "Use: `start:end` (in seconds)"
            )
            return
        
        start_time = int(parts[0])
        end_time = int(parts[1])
        
        if start_time < 0 or end_time <= start_time:
            await message.reply_text(
                "❌ **Invalid time range!**\n\n"
                "End time must be greater than start time."
            )
            return
        
        # Save trim settings
        trim_settings = {
            "start": start_time,
            "end": end_time,
            "duration": end_time - start_time
        }
        
        await db.set_trim_settings(user_id, trim_settings)
        
        # Check if user has already sent a video (stored in temp_files)
        temp_files = user.get("temp_files", [])
        video_file = next((f for f in temp_files if f.get("type") == "video"), None)
        
        if video_file:
            # Video already sent! Process it now
            await message.reply_text(
                f"✅ **Trim Settings Saved!**\n\n"
                f"⏱️ Start: {start_time}s\n"
                f"⏱️ End: {end_time}s\n"
                f"⏱️ Duration: {trim_settings['duration']}s\n\n"
                f"⚙️ Processing your video now..."
            )
            
            # Get the original video message and process it
            try:
                from pyrogram import Client
                video_msg = await client.get_messages(
                    video_file["chat_id"],
                    video_file["message_id"]
                )
                
                # Import handle_trim from media_handler
                from bot.plugins.media_handler import handle_trim
                
                # Refresh user data to get trim settings
                user = await db.get_user(user_id)
                
                # Process the trim
                await handle_trim(client, video_msg, user, trim_settings)
                
            except Exception as e:
                print(f"Error processing stored video: {e}")
                await message.reply_text(
                    f"❌ **Error processing stored video.**\n\n"
                    f"Please send the video file again."
                )
        else:
            await message.reply_text(
                f"✅ **Trim Settings Saved!**\n\n"
                f"⏱️ Start: {start_time}s\n"
                f"⏱️ End: {end_time}s\n"
                f"⏱️ Duration: {trim_settings['duration']}s\n\n"
                f"📹 Now send a video file to trim."
            )
        
    except ValueError:
        await message.reply_text(
            "❌ **Invalid numbers!**\n\n"
            "Use integers only.\n"
            "Example: `10:120`"
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")

@Client.on_message(filters.command("clearthumb") & filters.private)
async def clear_thumbnail(client: Client, message: Message):
    """Clear user's thumbnail"""
    user_id = message.from_user.id
    
    try:
        user = await db.get_user(user_id)
        if user:
            thumbnail_path = user.get("settings", {}).get("thumbnail")
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            
            await db.update_user_setting(user_id, "thumbnail", None)
            await message.reply_text("✅ **Thumbnail Cleared!**")
        else:
            await message.reply_text("❌ No thumbnail set.")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")

@Client.on_message(filters.command("defaultname") & filters.private)
async def reset_filename(client: Client, message: Message):
    """Reset filename to default"""
    user_id = message.from_user.id
    
    try:
        await db.update_user_setting(user_id, "filename", "default")
        await message.reply_text("✅ **Filename reset to default!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")
