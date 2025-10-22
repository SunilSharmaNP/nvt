from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_buttons():
    """Main menu buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("⚙️ User Settings", callback_data="user_settings")
        ],
        [
            InlineKeyboardButton("🎬 Video Tools", callback_data="video_tools")
        ],
        [
            InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")
        ]
    ])

def user_settings_buttons():
    """User settings menu buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 Send as Document/Video", callback_data="setting_send_as")
        ],
        [
            InlineKeyboardButton("🖼️ Thumbnail Set", callback_data="setting_thumbnail")
        ],
        [
            InlineKeyboardButton("📝 New Filename", callback_data="setting_filename")
        ],
        [
            InlineKeyboardButton("📋 Metadata", callback_data="setting_metadata")
        ],
        [
            InlineKeyboardButton("⬇️ Download Mode", callback_data="setting_download_mode")
        ],
        [
            InlineKeyboardButton("⬆️ Upload Mode", callback_data="setting_upload_mode")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ])

def video_tools_buttons():
    """Video tools menu buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 Video Merge", callback_data="tool_merge")
        ],
        [
            InlineKeyboardButton("🎞️ Video Encoding", callback_data="tool_encoding")
        ],
        [
            InlineKeyboardButton("🔄 Convert (Doc↔Video)", callback_data="tool_convert")
        ],
        [
            InlineKeyboardButton("©️ Watermark on Video", callback_data="tool_watermark")
        ],
        [
            InlineKeyboardButton("✂️ Trim Video", callback_data="tool_trim")
        ],
        [
            InlineKeyboardButton("🎬 Sample Video", callback_data="tool_sample")
        ],
        [
            InlineKeyboardButton("📊 MediaInfo", callback_data="tool_mediainfo")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ])

def merge_type_buttons():
    """Merge type selection buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎥 Video + Video", callback_data="merge_video_video")
        ],
        [
            InlineKeyboardButton("🎵 Video + Audio", callback_data="merge_video_audio")
        ],
        [
            InlineKeyboardButton("💬 Video + Subtitles", callback_data="merge_video_subs")
        ],
        [
            InlineKeyboardButton("🔙 Back to Video Tools", callback_data="video_tools")
        ]
    ])

def encoding_quality_buttons():
    """Video encoding quality selection buttons"""
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
            InlineKeyboardButton("360p", callback_data="quality_360p")
        ],
        [
            InlineKeyboardButton("⚙️ Custom Quality", callback_data="quality_custom")
        ],
        [
            InlineKeyboardButton("🔙 Back to Video Tools", callback_data="video_tools")
        ]
    ])

def encoding_settings_buttons():
    """Encoding settings configuration buttons"""
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
            InlineKeyboardButton("Pixel Format", callback_data="enc_pixel_format")
        ],
        [
            InlineKeyboardButton("✅ Done - Start Processing", callback_data="enc_done")
        ],
        [
            InlineKeyboardButton("🔙 Back to Quality Selection", callback_data="tool_encoding")
        ]
    ])

def send_as_buttons(current: str):
    """Send as document/video selection"""
    buttons = []
    for option in ["document", "video"]:
        text = f"{'✅' if current == option else '⭕'} {option.title()}"
        buttons.append([InlineKeyboardButton(text, callback_data=f"sendas_{option}")])
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="user_settings")])
    return InlineKeyboardMarkup(buttons)

def download_mode_buttons(current: str):
    """Download mode selection"""
    buttons = []
    for option in ["telegram", "url"]:
        text = f"{'✅' if current == option else '⭕'} {option.upper()}"
        buttons.append([InlineKeyboardButton(text, callback_data=f"dlmode_{option}")])
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="user_settings")])
    return InlineKeyboardMarkup(buttons)

def upload_mode_buttons(current: str):
    """Upload mode selection"""
    buttons = []
    for option in ["telegram", "gofile"]:
        text = f"{'✅' if current == option else '⭕'} {option.title()}"
        buttons.append([InlineKeyboardButton(text, callback_data=f"upmode_{option}")])
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="user_settings")])
    return InlineKeyboardMarkup(buttons)

def metadata_buttons(current: bool):
    """Metadata enable/disable buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{'✅' if current else '⭕'} Enable", callback_data="metadata_true"),
            InlineKeyboardButton(f"{'✅' if not current else '⭕'} Disable", callback_data="metadata_false")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="user_settings")
        ]
    ])

def back_to_main():
    """Simple back to main menu button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ])
