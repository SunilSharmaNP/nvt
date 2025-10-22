from config import Config
from bot.database import db

async def is_admin(user_id: int) -> bool:
    """Check if user is admin/sudo user"""
    return user_id == Config.OWNER_ID or user_id in Config.SUDO_USERS

async def can_use_in_private(user_id: int) -> bool:
    """Check if user can use bot in private chat"""
    return await is_admin(user_id)

async def is_authorized_group(chat_id: int) -> bool:
    """Check if chat is an authorized group"""
    return chat_id in Config.AUTHORIZED_GROUPS or chat_id < 0 and await db.is_group_authorized(chat_id)

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return filename.rsplit('.', 1)[-1] if '.' in filename else ''

def is_video_file(filename: str) -> bool:
    """Check if file is a video"""
    video_extensions = ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'webm', 'm4v', '3gp']
    return get_file_extension(filename).lower() in video_extensions

def is_audio_file(filename: str) -> bool:
    """Check if file is audio"""
    audio_extensions = ['mp3', 'aac', 'flac', 'wav', 'ogg', 'm4a', 'opus']
    return get_file_extension(filename).lower() in audio_extensions

def is_subtitle_file(filename: str) -> bool:
    """Check if file is subtitle"""
    subtitle_extensions = ['srt', 'ass', 'ssa', 'vtt', 'sub']
    return get_file_extension(filename).lower() in subtitle_extensions
