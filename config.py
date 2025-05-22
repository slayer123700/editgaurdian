import os

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "123456789").split(",")))
BOT_NAME = os.environ.get("BOT_NAME", "Edit-chan ✨")
BOT_OWNER_USERNAME = os.environ.get("BOT_OWNER_USERNAME", "your_username")
SUPPORT_GROUP_LINK = os.environ.get("SUPPORT_GROUP_LINK", "https://t.me/your_support_group")
