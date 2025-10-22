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
        # Check if user exists
        existing_user = await self.users.find_one({"user_id": user_id})
        
        if existing_user:
            # User exists - only update username and last_used
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
            # New user - create with defaults
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
    
    async def set_user_active(self, user_id: int, group_id: int, is_active: bool):
        """Set user active/hold mode in a specific group"""
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"active_in_group_{group_id}": is_active,
                    "last_used": datetime.utcnow()
                }
            }
        )
    
    async def is_user_active(self, user_id: int, group_id: int) -> bool:
        """Check if user is in active mode in a specific group"""
        user = await self.get_user(user_id)
        if user:
            return user.get(f"active_in_group_{group_id}", False)
        return False
    
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
            {"$set": {"temp_files": [], "video_tool_selected": None, "merge_type": None}}
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
