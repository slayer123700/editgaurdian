import motor.motor_asyncio
import os

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["edit_guardian_bot"]

# Collections
groups_collection = db["groups"]
users_collection = db["users"]
banned_users_collection = db["banned_users"]
broadcast_collection = db["broadcast_logs"]

# Group-related functions
async def add_group_if_not_exists(group_id, group_name=None):
    existing = await groups_collection.find_one({"group_id": group_id})
    if not existing:
        await groups_collection.insert_one({
            "group_id": group_id,
            "group_name": group_name or "Unknown",
            "delay": 5  # default delay in seconds
        })

async def is_group_exist(group_id):
    group = await groups_collection.find_one({"group_id": group_id})
    return group is not None

async def get_edit_delay(group_id):
    group = await groups_collection.find_one({"group_id": group_id})
    return group.get("delay", 5) if group else 5

async def set_edit_delay(group_id, delay: int):
    await groups_collection.update_one(
        {"group_id": group_id},
        {"$set": {"delay": delay}},
        upsert=True
    )

async def get_all_groups():
    return groups_collection.find()

# User-related functions
async def add_user_if_not_exists(user_id, name=None):
    existing = await users_collection.find_one({"user_id": user_id})
    if not existing:
        await users_collection.insert_one({
            "user_id": user_id,
            "name": name or "Unknown"
        })

async def get_all_users():
    return users_collection.find()

# Banned users
async def is_user_banned(user_id):
    return await banned_users_collection.find_one({"user_id": user_id}) is not None

async def ban_user(user_id):
    await banned_users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def unban_user(user_id):
    await banned_users_collection.delete_one({"user_id": user_id})

# Broadcast logging
async def log_broadcast(user_id, message_id):
    await broadcast_collection.insert_one({
        "user_id": user_id,
        "message_id": message_id
    })
