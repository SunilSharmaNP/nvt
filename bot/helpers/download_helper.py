import os
import aiohttp
import aiofiles
from pyrogram.types import Message
from pyrogram import Client
from config import Config
import time
from bot.utils.helpers import format_size, format_time

class DownloadHelper:
    @staticmethod
    async def download_telegram_file(client: Client, message: Message, file_path: str, status_msg=None):
        """Download file from Telegram with progress tracking"""
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
                        f"⏬ **Downloading from TG...**\n\n"
                        f"📊 Progress: {percentage:.1f}%\n"
                        f"📦 Size: {format_size(current)} / {format_size(total)}\n"
                        f"⚡ Speed: {format_size(speed)}/s\n"
                        f"⏰ ETA: {format_time(eta)}"
                    )
                    try:
                        await status_msg.edit_text(progress_text)
                    except:
                        pass

            if message.video:
                await client.download_media(message.video, file_path, progress=progress)
            elif message.document:
                await client.download_media(message.document, file_path, progress=progress)
            elif message.audio:
                await client.download_media(message.audio, file_path, progress=progress)
            elif message.photo:
                await client.download_media(message.photo, file_path, progress=progress)
            else:
                return None

            return file_path
        except Exception as e:
            print(f"Error downloading from Telegram: {e}")
            return None

    @staticmethod
    async def download_from_url(url: str, file_path: str, status_msg=None):
        """Download file from URL with progress tracking"""
        try:
            start_time = time.time()
            last_update = [0]

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None

                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)

                            if status_msg and total_size > 0 and (time.time() - last_update[0]) > 2:
                                last_update[0] = time.time()
                                percentage = (downloaded / total_size) * 100
                                elapsed = time.time() - start_time
                                speed = downloaded / (elapsed if elapsed > 0 else 1)
                                eta = (total_size - downloaded) / speed if speed > 0 else 0
                                
                                progress_text = (
                                    f"⏬ **Downloading from URL...**\n\n"
                                    f"📊 Progress: {percentage:.1f}%\n"
                                    f"📦 Size: {format_size(downloaded)} / {format_size(total_size)}\n"
                                    f"⚡ Speed: {format_size(speed)}/s\n"
                                    f"⏰ ETA: {format_time(eta)}"
                                )
                                try:
                                    await status_msg.edit_text(progress_text)
                                except:
                                    pass

            return file_path
        except Exception as e:
            print(f"Error downloading from URL: {e}")
            return None
                    
