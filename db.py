from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["edit_guardian_bot"]
chats = db["chats"]

def is_logging_enabled(chat_id):
    chat = chats.find_one({"chat_id": chat_id})
    return chat.get("logging", False) if chat else False

def toggle_logging(chat_id):
    chat = chats.find_one({"chat_id": chat_id})
    new_status = not chat.get("logging", False) if chat else True
    chats.update_one({"chat_id": chat_id}, {"$set": {"logging": new_status}}, upsert=True)
    return new_status

def save_chat(chat_id, chat_type):
    if not chats.find_one({"chat_id": chat_id}):
        chats.insert_one({"chat_id": chat_id, "type": chat_type, "logging": False, "delay": 5})

def get_stats():
    groups = chats.count_documents({"type": "group"})
    users = chats.count_documents({"type": "private"})
    return groups, users

def set_deletion_delay(chat_id, seconds):
    chats.update_one({"chat_id": chat_id}, {"$set": {"delay": seconds}}, upsert=True)

def get_deletion_delay(chat_id):
    data = chats.find_one({"chat_id": chat_id})
    return data.get("delay", 5)

def get_all_chats():
    return list(chats.find({}))
restricted_users = db["restricted"]

def add_restricted_user(user_id):
    restricted_users.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

def remove_restricted_user(user_id):
    restricted_users.delete_one({"user_id": user_id})

def get_restricted_users():
    return [doc["user_id"] for doc in restricted_users.find({})]

