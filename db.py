from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.edit_guardian

async def add_user(user_id):
    db.users.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def add_chat(chat_id):
    db.chats.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)

async def get_all_users():
    return [u["user_id"] for u in db.users.find()]

async def get_all_chats():
    return [c["chat_id"] for c in db.chats.find()]

async def add_restricted_user(user_id):
    db.restricted.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def remove_restricted_user(user_id):
    db.restricted.delete_one({"user_id": user_id})

async def is_user_restricted(user_id):
    return db.restricted.find_one({"user_id": user_id}) is not None

async def get_restricted_users():
    return [u["user_id"] for u in db.restricted.find()]

async def set_delay(chat_id, seconds):
    db.delays.update_one({"chat_id": chat_id}, {"$set": {"seconds": seconds}}, upsert=True)

async def get_delay(chat_id):
    data = db.delays.find_one({"chat_id": chat_id})
    return data["seconds"] if data else 5
