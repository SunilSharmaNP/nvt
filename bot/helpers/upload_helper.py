import os
import aiohttp
import aiofiles
from pyrogram import Client
from config import Config
import time
from bot.utils.helpers import format_size, format_time

class UploadHelper:
    @staticmethod
    async def upload_to_telegram(client: Client, chat_id: int, file_path: str, thumb_path: str = None,
                                caption: str = "", as_document: bool = True, status_msg=None):
        """Upload file to Telegram with progress tracking"""
        try:
            start_time = time.time()
            last_update = [0]

            async def progress(current, total):
                percentage = (current / total) * 100
                elapsed = time.time() - start_time
                speed = current / (elapsed if elapsed > 0 else 1)
                eta = (total - current) / speed if speed > 0 else 0
                
                if status_msg and (time.time() - last_update[0]) > 2:
                    last_update[0] = time.time()
                    progress_text = (
                        f"⏫ **Uploading to TG...**\n\n"
                        f"📊 Progress: {percentage:.1f}%\n"
                        f"📦 Size: {format_size(current)} / {format_size(total)}\n"
                        f"⚡ Speed: {format_size(speed)}/s\n"
                        f"⏰ ETA: {format_time(eta)}"
                    )
                    try:
                        await status_msg.edit_text(progress_text)
                    except:
                        pass

            if as_document:
                return await client.send_document(
                    chat_id=chat_id,
                    document=file_path,
                    thumb=thumb_path,
                    caption=caption,
                    progress=progress
                )
            else:
                return await client.send_video(
                    chat_id=chat_id,
                    video=file_path,
                    thumb=thumb_path,
                    caption=caption,
                    progress=progress,
                    supports_streaming=True
                )
        except Exception as e:
            print(f"Error uploading to Telegram: {e}")
            if status_msg:
                try:
                    await status_msg.edit_text(f"❌ **Upload Error:**\n{str(e)}")
                except:
                    pass
            return None

    @staticmethod
    async def upload_to_gofile(file_path: str, status_msg=None):
        """Upload file to GoFile server"""
        try:
            if status_msg:
                await status_msg.edit_text("⏫ **Uploading to GoFile...**\n\nGetting server...")

            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.gofile.io/getServer") as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if data["status"] != "ok":
                        return None
                    server = data["data"]["server"]

                if status_msg:
                    await status_msg.edit_text("⏫ **Uploading to GoFile...**\n\nUploading file...")

                file_size = os.path.getsize(file_path)

                async with aiofiles.open(file_path, 'rb') as f:
                    file_data = await f.read()

                form = aiohttp.FormData()
                form.add_field('file', file_data, filename=os.path.basename(file_path))

                upload_url = f"https://{server}.gofile.io/uploadFile"

                async with session.post(upload_url, data=form) as response:
                    if response.status != 200:
                        return None

                    result = await response.json()
                    if result["status"] == "ok":
                        return result["data"]["downloadPage"]
                    return None
        except Exception as e:
            print(f"Error uploading to GoFile: {e}")
            return None
            
