import asyncio
import os
import subprocess
import json
from typing import Dict, Optional, Tuple
from config import Config

class FFmpegHelper:
    @staticmethod
    async def get_video_info(file_path: str) -> Optional[Dict]:
        """Get video information using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            return json.loads(stdout.decode())
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    @staticmethod
    async def encode_video(input_file: str, output_file: str, settings: Dict, progress_callback=None) -> bool:
        """Encode video with specified settings"""
        try:
            cmd = ["ffmpeg", "-i", input_file]
            
            # Video codec
            cmd.extend(["-c:v", settings.get("codec", "libx264")])
            
            # CRF
            if "crf" in settings:
                cmd.extend(["-crf", str(settings["crf"])])
            
            # Resolution
            if "resolution" in settings:
                cmd.extend(["-vf", f"scale={settings['resolution']}"])
            
            # Preset
            if "preset" in settings:
                cmd.extend(["-preset", settings["preset"]])
            
            # Audio codec
            cmd.extend(["-c:a", settings.get("audio_codec", "aac")])
            
            # Audio bitrate
            if "audio_bitrate" in settings:
                cmd.extend(["-b:a", settings["audio_bitrate"]])
            
            # Pixel format
            if "pixel_format" in settings:
                cmd.extend(["-pix_fmt", settings["pixel_format"]])
            
            # Threads
            cmd.extend(["-threads", str(Config.FFMPEG_THREADS)])
            
            # Output
            cmd.extend(["-y", output_file])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            print(f"Error encoding video: {e}")
            return False
    
    @staticmethod
    async def merge_video_video(video1: str, video2: str, output: str) -> bool:
        """Merge two videos"""
        try:
            # Create concat file
            concat_file = f"{output}.txt"
            with open(concat_file, "w") as f:
                f.write(f"file '{video1}'\n")
                f.write(f"file '{video2}'\n")
            
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-y", output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            os.remove(concat_file)
            return process.returncode == 0
        except Exception as e:
            print(f"Error merging videos: {e}")
            return False
    
    @staticmethod
    async def merge_video_audio(video: str, audio: str, output: str) -> bool:
        """Merge video with audio"""
        try:
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", audio,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-y", output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            print(f"Error merging video and audio: {e}")
            return False
    
    @staticmethod
    async def merge_video_subtitle(video: str, subtitle: str, output: str) -> bool:
        """Merge video with subtitle"""
        try:
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", subtitle,
                "-c", "copy",
                "-c:s", "mov_text",
                "-y", output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            print(f"Error merging video and subtitle: {e}")
            return False
    
    @staticmethod
    async def add_watermark(video: str, watermark: str, output: str, position: str = "topright") -> bool:
        """Add watermark to video"""
        try:
            positions = {
                "topleft": "10:10",
                "topright": "W-w-10:10",
                "bottomleft": "10:H-h-10",
                "bottomright": "W-w-10:H-h-10",
                "center": "(W-w)/2:(H-h)/2"
            }
            
            overlay_pos = positions.get(position, positions["topright"])
            
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", watermark,
                "-filter_complex", f"overlay={overlay_pos}",
                "-c:a", "copy",
                "-y", output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return False
    
    @staticmethod
    async def trim_video(video: str, output: str, start_time: str, duration: str) -> bool:
        """Trim video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", video,
                "-ss", start_time,
                "-t", duration,
                "-c", "copy",
                "-y", output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            print(f"Error trimming video: {e}")
            return False
    
    @staticmethod
    async def generate_sample(video: str, output: str, duration: int = 30) -> bool:
        """Generate sample video"""
        try:
            # Get video info first
            info = await FFmpegHelper.get_video_info(video)
            if not info:
                return False
            
            total_duration = float(info["format"]["duration"])
            start_time = max(0, (total_duration - duration) / 2)
            
            cmd = [
                "ffmpeg",
                "-i", video,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",
                "-y", output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            print(f"Error generating sample: {e}")
            return False
    
    @staticmethod
    async def get_mediainfo_text(video: str) -> str:
        """Get detailed media info as text"""
        try:
            info = await FFmpegHelper.get_video_info(video)
            if not info:
                return "❌ Unable to get media info"
            
            format_info = info.get("format", {})
            video_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
            audio_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), {})
            
            text = "📊 **Media Information**\n\n"
            text += f"📁 **File**: {os.path.basename(video)}\n"
            text += f"📦 **Size**: {int(format_info.get('size', 0)) / (1024*1024):.2f} MB\n"
            text += f"⏱ **Duration**: {float(format_info.get('duration', 0)):.2f} seconds\n"
            text += f"🎞 **Format**: {format_info.get('format_name', 'N/A')}\n\n"
            
            if video_stream:
                text += "🎥 **Video Stream**\n"
                text += f"  • Codec: {video_stream.get('codec_name', 'N/A')}\n"
                text += f"  • Resolution: {video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}\n"
                text += f"  • FPS: {eval(video_stream.get('r_frame_rate', '0/1')):.2f}\n"
                text += f"  • Bitrate: {int(video_stream.get('bit_rate', 0)) / 1000:.0f} kbps\n\n"
            
            if audio_stream:
                text += "🎵 **Audio Stream**\n"
                text += f"  • Codec: {audio_stream.get('codec_name', 'N/A')}\n"
                text += f"  • Sample Rate: {audio_stream.get('sample_rate', 'N/A')} Hz\n"
                text += f"  • Channels: {audio_stream.get('channels', 'N/A')}\n"
                text += f"  • Bitrate: {int(audio_stream.get('bit_rate', 0)) / 1000:.0f} kbps\n"
            
            return text
        except Exception as e:
            return f"❌ Error getting media info: {str(e)}"
    
    @staticmethod
    async def generate_thumbnail(video: str, output: str, time: str = "00:00:01") -> bool:
        """Generate thumbnail from video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", video,
                "-ss", time,
                "-vframes", "1",
                "-y", output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return False
