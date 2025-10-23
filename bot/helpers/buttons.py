from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_buttons():
    """Main menu buttons - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("⚙️ User Settings", callback_data="user_settings"),
            InlineKeyboardButton("🎬 Video Tools", callback_data="video_tools")
        ],
        [
            InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot"),
            InlineKeyboardButton("📊 Status", callback_data="help")
        ]
    ])

def user_settings_buttons():
    """User settings menu buttons - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 Send As", callback_data="setting_send_as"),
            InlineKeyboardButton("🖼️ Thumbnail", callback_data="setting_thumbnail")
        ],
        [
            InlineKeyboardButton("📝 Filename", callback_data="setting_filename"),
            InlineKeyboardButton("📋 Metadata", callback_data="setting_metadata")
        ],
        [
            InlineKeyboardButton("⬇️ Download Mode", callback_data="setting_download_mode"),
            InlineKeyboardButton("⬆️ Upload Mode", callback_data="setting_upload_mode")
        ],
        [
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"),
            InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")
        ]
    ])

def video_tools_buttons():
    """Video tools menu buttons - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 Video Merge", callback_data="tool_merge"),
            InlineKeyboardButton("🎞️ Video Encoding", callback_data="tool_encoding")
        ],
        [
            InlineKeyboardButton("🔄 Convert", callback_data="tool_convert"),
            InlineKeyboardButton("©️ Watermark", callback_data="tool_watermark")
        ],
        [
            InlineKeyboardButton("✂️ Trim Video", callback_data="tool_trim"),
            InlineKeyboardButton("🎬 Sample Video", callback_data="tool_sample")
        ],
        [
            InlineKeyboardButton("📊 MediaInfo", callback_data="tool_mediainfo"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def merge_type_buttons():
    """Merge type selection buttons - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎥 Video + Video", callback_data="merge_video_video"),
            InlineKeyboardButton("🎵 Video + Audio", callback_data="merge_video_audio")
        ],
        [
            InlineKeyboardButton("💬 Video + Subtitles", callback_data="merge_video_subs"),
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools")
        ]
    ])

def encoding_quality_buttons():
    """Video encoding quality selection buttons - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1080p", callback_data="quality_1080p"),
            InlineKeyboardButton("1080p HEVC", callback_data="quality_1080p_hevc")
        ],
        [
            InlineKeyboardButton("720p", callback_data="quality_720p"),
            InlineKeyboardButton("720p HEVC", callback_data="quality_720p_hevc")
        ],
        [
            InlineKeyboardButton("480p", callback_data="quality_480p"),
            InlineKeyboardButton("480p HEVC", callback_data="quality_480p_hevc")
        ],
        [
            InlineKeyboardButton("360p", callback_data="quality_360p"),
            InlineKeyboardButton("⚙️ Custom", callback_data="quality_custom")
        ],
        [
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def encoding_settings_buttons():
    """Encoding settings configuration buttons - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("CRF", callback_data="enc_crf"),
            InlineKeyboardButton("Audio Bitrate", callback_data="enc_audio_bitrate")
        ],
        [
            InlineKeyboardButton("Resolution", callback_data="enc_resolution"),
            InlineKeyboardButton("Preset", callback_data="enc_preset")
        ],
        [
            InlineKeyboardButton("Video Codec", callback_data="enc_video_codec"),
            InlineKeyboardButton("Audio Codec", callback_data="enc_audio_codec")
        ],
        [
            InlineKeyboardButton("✅ Done", callback_data="enc_done"),
            InlineKeyboardButton("🔙 Quality Selection", callback_data="tool_encoding")
        ]
    ])

def watermark_position_buttons():
    """Watermark position selection - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("↖️ Top Left", callback_data="wm_topleft"),
            InlineKeyboardButton("↗️ Top Right", callback_data="wm_topright")
        ],
        [
            InlineKeyboardButton("↙️ Bottom Left", callback_data="wm_bottomleft"),
            InlineKeyboardButton("↘️ Bottom Right", callback_data="wm_bottomright")
        ],
        [
            InlineKeyboardButton("⭕ Center", callback_data="wm_center"),
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools")
        ]
    ])

def send_as_buttons(current: str):
    """Send as document/video selection - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{'✅' if current == 'document' else '⭕'} Document", callback_data="sendas_document"),
            InlineKeyboardButton(f"{'✅' if current == 'video' else '⭕'} Video", callback_data="sendas_video")
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def download_mode_buttons(current: str):
    """Download mode selection - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{'✅' if current == 'telegram' else '⭕'} Telegram", callback_data="dlmode_telegram"),
            InlineKeyboardButton(f"{'✅' if current == 'url' else '⭕'} URL", callback_data="dlmode_url")
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def upload_mode_buttons(current: str):
    """Upload mode selection - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{'✅' if current == 'telegram' else '⭕'} Telegram", callback_data="upmode_telegram"),
            InlineKeyboardButton(f"{'✅' if current == 'gofile' else '⭕'} GoFile", callback_data="upmode_gofile")
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def metadata_buttons(current: bool):
    """Metadata enable/disable buttons - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{'✅' if current else '⭕'} Enable", callback_data="metadata_true"),
            InlineKeyboardButton(f"{'✅' if not current else '⭕'} Disable", callback_data="metadata_false")
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def back_to_main():
    """Back to main menu button - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"),
            InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")
        ]
    ])

def back_to_video_tools():
    """Back to video tools button - 2 column layout"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])
    
