from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from typing import Dict, Optional, List
from datetime import datetime

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.users = self.db.users
        self.tasks = self.db.tasks
        self.groups = self.db.groups

    async def add_user(self, user_id: int, username: str = None):
        """Add a new user or update existing user"""
        existing_user = await self.users.find_one({"user_id": user_id})

        if existing_user:
            await self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "last_used": datetime.utcnow()
                    }
                }
            )
        else:
            user_data = {
                "user_id": user_id,
                "username": username,
                "settings": Config.DEFAULT_SETTINGS.copy(),
                "is_active": False,
                "is_banned": False,
                "video_tool_selected": None,
                "encoding_settings": None,
                "merge_type": None,
                "temp_files": [],
                "watermark_type": None,
                "watermark_text": None,
                "watermark_image_file_id": None,
                "watermark_position": "topright",
                "trim_settings": None,
                "sample_duration": 30,
                "convert_mode": "to_document",
                "thumbnail_file_id": None,
                "custom_filename": None,
                "created_at": datetime.utcnow(),
                "last_used": datetime.utcnow()
            }
            await self.users.insert_one(user_data)

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        return await self.users.find_one({"user_id": user_id})

    async def update_user_settings(self, user_id: int, settings: Dict):
        """Update user settings"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"settings": settings, "last_used": datetime.utcnow()}}
        )

    async def set_user_active(self, user_id: int, is_active: bool, group_id: int = None):
        """Set user active/hold mode"""
        update_data = {
            "is_active": is_active,
            "last_used": datetime.utcnow()
        }
        if group_id:
            update_data[f"active_in_group_{group_id}"] = is_active
        
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )

    async def is_user_active(self, user_id: int, group_id: int = None) -> bool:
        """Check if user is in active mode"""
        user = await self.get_user(user_id)
        if not user:
            return False
        
        if group_id:
            return user.get(f"active_in_group_{group_id}", False)
        return user.get("is_active", False)

    async def set_video_tool(self, user_id: int, tool: str):
        """Set selected video tool for user"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"video_tool_selected": tool, "last_used": datetime.utcnow()}}
        )

    async def set_encoding_settings(self, user_id: int, settings: Dict):
        """Set encoding settings for user"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"encoding_settings": settings, "last_used": datetime.utcnow()}}
        )

    async def set_merge_type(self, user_id: int, merge_type: str):
        """Set merge type for user"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"merge_type": merge_type, "last_used": datetime.utcnow()}}
        )

    async def set_watermark_type(self, user_id: int, wm_type: str):
        """Set watermark type (text/image)"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"watermark_type": wm_type, "last_used": datetime.utcnow()}}
        )

    async def set_watermark_text(self, user_id: int, text: str):
        """Set watermark text"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"watermark_text": text, "last_used": datetime.utcnow()}}
        )

    async def set_watermark_image(self, user_id: int, file_id: str):
        """Set watermark image file ID"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"watermark_image_file_id": file_id, "last_used": datetime.utcnow()}}
        )

    async def set_watermark_position(self, user_id: int, position: str):
        """Set watermark position"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"watermark_position": position, "last_used": datetime.utcnow()}}
        )

    async def set_trim_settings(self, user_id: int, settings: Dict):
        """Set trim settings"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"trim_settings": settings, "last_used": datetime.utcnow()}}
        )

    async def set_sample_duration(self, user_id: int, duration: int):
        """Set sample video duration"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"sample_duration": duration, "last_used": datetime.utcnow()}}
        )

    async def set_convert_mode(self, user_id: int, mode: str):
        """Set convert mode (to_document/to_video)"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"convert_mode": mode, "last_used": datetime.utcnow()}}
        )

    async def set_thumbnail(self, user_id: int, file_id: str):
        """Set thumbnail file ID"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"thumbnail_file_id": file_id, "last_used": datetime.utcnow()}}
        )

    async def set_custom_filename(self, user_id: int, filename: str):
        """Set custom filename"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"custom_filename": filename, "last_used": datetime.utcnow()}}
        )

    async def add_temp_file(self, user_id: int, file_info: Dict):
        """Add temporary file to user's collection"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$push": {"temp_files": file_info}}
        )

    async def get_temp_files(self, user_id: int) -> List[Dict]:
        """Get user's temporary files"""
        user = await self.get_user(user_id)
        return user.get("temp_files", []) if user else []

    async def clear_temp_files(self, user_id: int):
        """Clear user's temporary files"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"temp_files": []}}
        )

    async def clear_all_user_data(self, user_id: int):
        """Clear all user tool selections and temp data"""
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "video_tool_selected": None,
                    "merge_type": None,
                    "encoding_settings": None,
                    "trim_settings": None,
                    "temp_files": [],
                    "last_used": datetime.utcnow()
                }
            }
        )

    async def add_task(self, user_id: int, task_type: str, status: str = "processing"):
        """Add a new task"""
        task_data = {
            "user_id": user_id,
            "task_type": task_type,
            "status": status,
            "started_at": datetime.utcnow(),
            "progress": 0
        }
        result = await self.tasks.insert_one(task_data)
        return str(result.inserted_id)

    async def get_user_task(self, user_id: int) -> Optional[Dict]:
        """Get active task for user"""
        return await self.tasks.find_one({"user_id": user_id, "status": "processing"})

    async def get_all_active_tasks(self) -> List[Dict]:
        """Get all active tasks"""
        cursor = self.tasks.find({"status": "processing"})
        return await cursor.to_list(length=None)

    async def update_task_progress(self, task_id: str, progress: int):
        """Update task progress"""
        from bson import ObjectId
        await self.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"progress": progress}}
        )

    async def complete_task(self, task_id: str):
        """Mark task as completed"""
        from bson import ObjectId
        await self.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": "completed", "completed_at": datetime.utcnow()}}
        )

    async def cancel_task(self, user_id: int):
        """Cancel user's active task"""
        await self.tasks.update_many(
            {"user_id": user_id, "status": "processing"},
            {"$set": {"status": "cancelled", "completed_at": datetime.utcnow()}}
        )

    async def is_group_authorized(self, group_id: int) -> bool:
        """Check if group is authorized"""
        return group_id in Config.AUTHORIZED_GROUPS

    async def ban_user(self, user_id: int):
        """Ban a user"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": True}}
        )

    async def unban_user(self, user_id: int):
        """Unban a user"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_banned": False}}
        )

    async def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        user = await self.get_user(user_id)
        return user.get("is_banned", False) if user else False
