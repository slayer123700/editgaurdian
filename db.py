from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["edit_guardian_bot"]

users_col = db["users"]
groups_col = db["groups"]
restricted_col = db["restricted"]
settings_col = db["settings"]

# User Functions
def add_user(user_id):
    users_col.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

def get_all_users():
    return [doc["_id"] for doc in users_col.find()]

# Group Functions
def add_group(chat_id):
    groups_col.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)

def get_all_chats():
    return [doc["_id"] for doc in groups_col.find()]

# Restriction Functions
def add_restricted_user(user_id):
    restricted_col.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

def is_restricted(user_id):
    return restricted_col.find_one({"_id": user_id}) is not None

# Edit Delay Settings
def get_edit_delay(chat_id):
    data = settings_col.find_one({"_id": chat_id})
    return data.get("delay", 5) if data else 5

def set_edit_delay(chat_id, delay):
    settings_col.update_one({"_id": chat_id}, {"$set": {"delay": delay}}, upsert=True)
