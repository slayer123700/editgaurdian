import os
from pymongo import MongoClient

# Get Mongo URI from environment or use local fallback
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["edit_chan"]
settings_collection = db["group_settings"]

def is_logging_enabled(chat_id):
    result = settings_collection.find_one({"chat_id": chat_id})
    return result.get("logging_enabled", False) if result else False

def toggle_logging(chat_id):
    current = settings_collection.find_one({"chat_id": chat_id})
    if current:
        new_state = not current["logging_enabled"]
        settings_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"logging_enabled": new_state}}
        )
    else:
        new_state = True
        settings_collection.insert_one({
            "chat_id": chat_id,
            "logging_enabled": True
        })
    return new_state
