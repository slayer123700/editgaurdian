import os

# === Bot Settings ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Required: Bot token from @BotFather
OWNER_ID = int(os.environ.get("OWNER_ID"))  # Required: Telegram user ID of the bot owner

# === MongoDB Configuration ===
MONGO_URI = os.environ.get("MONGO_URI")  # Required: Your MongoDB URI

# === Optional Start Assets ===
START_IMAGE = os.environ.get("START_IMAGE", "")  # URL of the start image (optional)
PING_IMAGE = os.environ.get("PING_IMAGE", "")    # URL of the ping image (optional)
STATS_IMAGE = os.environ.get("STATS_IMAGE", "")  # URL of the stats image (optional)
START_VIDEO = os.environ.get("START_VIDEO", "")  # URL of the start video (optional)
PING_VIDEO = os.environ.get("PING_VIDEO", "")    # URL of the ping video (optional)

# === Support and Links ===
SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "https://t.me/YourSupportGroup")

# === Defaults ===
DEFAULT_DELETE_DELAY = int(os.environ.get("DEFAULT_DELETE_DELAY", 10))  # Default delay in seconds for message deletion
BOT_NAME = os.environ.get("BOT_NAME", "EditGuardianBot")
