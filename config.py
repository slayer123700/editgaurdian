import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Optional values (fill in directly or through environment variables)
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))  # replace with your Telegram ID
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "SLAYER1237")  # replace with your Telegram username
BOT_NAME = os.getenv("BOT_NAME", "EditGuardianBot")  # replace with your bot's name
