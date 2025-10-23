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
            InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")
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
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def video_tools_buttons(active_tool=None):
    """Video tools menu buttons with tick marks for active tool"""
    tools = [
        ("🔗 Video Merge", "tool_merge", "merge"),
        ("🎞️ Video Encoding", "tool_encoding", "encoding"),
        ("🔄 Convert", "tool_convert", "convert"),
        ("©️ Watermark", "tool_watermark", "watermark"),
        ("✂️ Trim Video", "tool_trim", "trim"),
        ("🎬 Sample Video", "tool_sample", "sample"),
        ("📊 MediaInfo", "tool_mediainfo", "mediainfo")
    ]
    
    buttons = []
    for i in range(0, len(tools), 2):
        row = []
        for j in range(2):
            if i + j < len(tools):
                name, callback, tool_id = tools[i + j]
                prefix = "✅ " if active_tool == tool_id else ""
                row.append(InlineKeyboardButton(f"{prefix}{name}", callback_data=callback))
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def merge_type_buttons(current=None):
    """Merge type selection buttons with tick marks"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅ ' if current == 'video_video' else ''}🎥 Video + Video", 
                callback_data="merge_video_video"
            ),
            InlineKeyboardButton(
                f"{'✅ ' if current == 'video_audio' else ''}🎵 Video + Audio", 
                callback_data="merge_video_audio"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅ ' if current == 'video_subs' else ''}💬 Video + Subtitles", 
                callback_data="merge_video_subs"
            ),
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools")
        ]
    ])

def encoding_quality_buttons(current=None):
    """Video encoding quality selection buttons with tick marks"""
    presets = [
        ("1080p", "quality_1080p"),
        ("1080p HEVC", "quality_1080p_hevc"),
        ("720p", "quality_720p"),
        ("720p HEVC", "quality_720p_hevc"),
        ("480p", "quality_480p"),
        ("480p HEVC", "quality_480p_hevc"),
        ("360p", "quality_360p"),
        ("⚙️ Custom", "quality_custom")
    ]
    
    buttons = []
    for i in range(0, len(presets), 2):
        row = []
        for j in range(2):
            if i + j < len(presets):
                name, callback = presets[i + j]
                preset_id = callback.replace("quality_", "")
                prefix = "✅ " if current == preset_id else ""
                row.append(InlineKeyboardButton(f"{prefix}{name}", callback_data=callback))
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(buttons)

def encoding_settings_buttons():
    """Encoding settings configuration buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Done", callback_data="enc_done"),
            InlineKeyboardButton("🔙 Quality", callback_data="tool_encoding")
        ]
    ])

def convert_mode_buttons(current=None):
    """Convert mode selection - to document or to video"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅ ' if current == 'to_document' else ''}📄 To Document", 
                callback_data="convert_to_document"
            ),
            InlineKeyboardButton(
                f"{'✅ ' if current == 'to_video' else ''}🎥 To Video", 
                callback_data="convert_to_video"
            )
        ],
        [
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def watermark_type_buttons(current=None):
    """Watermark type selection - text or PNG image"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅ ' if current == 'text' else ''}📝 Text Watermark", 
                callback_data="wm_type_text"
            ),
            InlineKeyboardButton(
                f"{'✅ ' if current == 'image' else ''}🖼️ PNG Watermark", 
                callback_data="wm_type_image"
            )
        ],
        [
            InlineKeyboardButton("📍 Position", callback_data="wm_position_menu")
        ],
        [
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def watermark_position_buttons(current=None):
    """Watermark position selection"""
    positions = [
        ("↖️ Top Left", "wm_pos_topleft", "topleft"),
        ("↗️ Top Right", "wm_pos_topright", "topright"),
        ("↙️ Bottom Left", "wm_pos_bottomleft", "bottomleft"),
        ("↘️ Bottom Right", "wm_pos_bottomright", "bottomright"),
        ("⭕ Center", "wm_pos_center", "center")
    ]
    
    buttons = []
    for i in range(0, len(positions), 2):
        row = []
        for j in range(2):
            if i + j < len(positions):
                name, callback, pos_id = positions[i + j]
                prefix = "✅ " if current == pos_id else ""
                row.append(InlineKeyboardButton(f"{prefix}{name}", callback_data=callback))
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton("🔙 Watermark", callback_data="tool_watermark"),
        InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools")
    ])
    return InlineKeyboardMarkup(buttons)

def sample_duration_buttons(current=None):
    """Sample video duration selection"""
    durations = [
        ("30s", "sample_30"),
        ("60s", "sample_60"),
        ("120s", "sample_120"),
        ("300s", "sample_300")
    ]
    
    buttons = []
    row = []
    for name, callback in durations:
        duration = callback.replace("sample_", "")
        prefix = "✅ " if current == int(duration) else ""
        row.append(InlineKeyboardButton(f"{prefix}{name}", callback_data=callback))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(buttons)

def send_as_buttons(current: str):
    """Send as document/video selection"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅' if current == 'document' else '⭕'} Document", 
                callback_data="sendas_document"
            ),
            InlineKeyboardButton(
                f"{'✅' if current == 'video' else '⭕'} Video", 
                callback_data="sendas_video"
            )
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def download_mode_buttons(current: str):
    """Download mode selection"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅' if current == 'telegram' else '⭕'} Telegram", 
                callback_data="dlmode_telegram"
            ),
            InlineKeyboardButton(
                f"{'✅' if current == 'url' else '⭕'} URL", 
                callback_data="dlmode_url"
            )
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def upload_mode_buttons(current: str):
    """Upload mode selection"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅' if current == 'telegram' else '⭕'} Telegram", 
                callback_data="upmode_telegram"
            ),
            InlineKeyboardButton(
                f"{'✅' if current == 'gofile' else '⭕'} GoFile", 
                callback_data="upmode_gofile"
            )
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def metadata_buttons(current: bool):
    """Metadata enable/disable buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅' if current else '⭕'} Enable", 
                callback_data="metadata_true"
            ),
            InlineKeyboardButton(
                f"{'✅' if not current else '⭕'} Disable", 
                callback_data="metadata_false"
            )
        ],
        [
            InlineKeyboardButton("🔙 Settings", callback_data="user_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def back_to_main():
    """Back to main menu button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ])

def back_to_video_tools():
    """Back to video tools button"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Video Tools", callback_data="video_tools"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
        ]
    ])

def cancel_button():
    """Cancel current operation"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_operation")]
    ])
