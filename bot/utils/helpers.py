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
    video_extensions = ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv', 'webm', 'm4v', '3gp', 'mpg', 'mpeg']
    return get_file_extension(filename).lower() in video_extensions

def is_audio_file(filename: str) -> bool:
    """Check if file is audio"""
    audio_extensions = ['mp3', 'aac', 'flac', 'wav', 'ogg', 'm4a', 'opus', 'wma']
    return get_file_extension(filename).lower() in audio_extensions

def is_subtitle_file(filename: str) -> bool:
    """Check if file is subtitle"""
    subtitle_extensions = ['srt', 'ass', 'ssa', 'vtt', 'sub']
    return get_file_extension(filename).lower() in subtitle_extensions

def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'gif']
    return get_file_extension(filename).lower() in image_extensions

def format_size(bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

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

def get_progress_bar(percentage: float, length: int = 10) -> str:
    """Generate progress bar"""
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percentage:.1f}%"

def time_to_seconds(time_str: str) -> int:
    """Convert time string (HH:MM:SS or MM:SS or SS) to seconds"""
    try:
        parts = time_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        else:  # SS
            return int(parts[0])
    except:
        return 0
