import os
import aiohttp
import aiofiles
from pyrogram.types import Message
from config import Config
import time

class DownloadHelper:
    @staticmethod
    async def download_telegram_file(client, message: Message, file_path: str, progress_callback=None):
        """Download file from Telegram"""
        try:
            start_time = time.time()
            
            async def progress(current, total):
                if progress_callback:
                    percentage = (current / total) * 100
                    speed = current / (time.time() - start_time + 1)
                    eta = (total - current) / speed if speed > 0 else 0
                    await progress_callback(percentage, speed, eta)
            
            if message.video:
                await client.download_media(message.video, file_path, progress=progress)
            elif message.document:
                await client.download_media(message.document, file_path, progress=progress)
            elif message.audio:
                await client.download_media(message.audio, file_path, progress=progress)
            else:
                return None
            
            return file_path
        except Exception as e:
            print(f"Error downloading from Telegram: {e}")
            return None
    
    @staticmethod
    async def download_from_url(url: str, file_path: str, progress_callback=None):
        """Download file from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    start_time = time.time()
                    
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size > 0:
                                percentage = (downloaded / total_size) * 100
                                speed = downloaded / (time.time() - start_time + 1)
                                eta = (total_size - downloaded) / speed if speed > 0 else 0
                                await progress_callback(percentage, speed, eta)
            
            return file_path
        except Exception as e:
            print(f"Error downloading from URL: {e}")
            return None
    
    @staticmethod
    def format_size(bytes: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} TB"
    
    @staticmethod
    def format_speed(bytes_per_sec: float) -> str:
        """Format speed to human readable"""
        return f"{DownloadHelper.format_size(bytes_per_sec)}/s"
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds to human readable time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
