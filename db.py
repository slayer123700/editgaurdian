from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client['editguardianbot']

users_collection = db['users']
chats_collection = db['chats']
restricted_users_collection = db['restricted_users']

# Add or update a user
def add_user(user_id):
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

# Add or update a chat (group)
def add_chat(chat_id):
    chats_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )

# Get all user IDs
def get_all_users():
    return [user["user_id"] for user in users_collection.find({}, {"_id": 0})]

# Get all chat IDs
def get_all_chats():
    return [chat["chat_id"] for chat in chats_collection.find({}, {"_id": 0})]

# Add restricted user
def add_restricted_user(user_id):
    restricted_users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

# Get all restricted user IDs
def get_restricted_users():
    return [user["user_id"] for user in restricted_users_collection.find({}, {"_id": 0})]
