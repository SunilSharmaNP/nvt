import os
import aiohttp
import aiofiles
from pyrogram.types import Message
from config import Config
import time

class UploadHelper:
    @staticmethod
    async def upload_to_telegram(client, chat_id: int, file_path: str, thumb_path: str = None, 
                                caption: str = "", as_document: bool = True, progress_callback=None):
        """Upload file to Telegram"""
        try:
            start_time = time.time()
            
            async def progress(current, total):
                if progress_callback:
                    percentage = (current / total) * 100
                    speed = current / (time.time() - start_time + 1)
                    eta = (total - current) / speed if speed > 0 else 0
                    await progress_callback(percentage, speed, eta)
            
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
            return None
    
    @staticmethod
    async def upload_to_gofile(file_path: str, progress_callback=None):
        """Upload file to GoFile server"""
        try:
            # Get best server
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.gofile.io/getServer") as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if data["status"] != "ok":
                        return None
                    server = data["data"]["server"]
                
                # Upload file
                file_size = os.path.getsize(file_path)
                start_time = time.time()
                
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
