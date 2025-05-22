import os
import time
import psutil
import platform
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

from db import (
    add_user, add_chat, get_bot_stats, get_delay, set_delay,
    add_restricted_user, remove_restricted_user, get_restricted_users
)

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))  # Replace with your real Telegram ID
ADMIN_IDS = [OWNER_ID]
START_TIME = time.time()

# ========== BASIC COMMANDS ==========

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if chat.type == "private":
        add_user(user.id)
    else:
        add_chat(chat.id)

    caption = (
        "🎀 *ʜᴇʏ ᴍᴀsᴛᴇʀ~!*\n\n"
        "• ɪ'ᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴛᴇxᴛ ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʙᴏᴛ.\n"
        "• ɪ sᴀғᴇɢᴜᴀʀᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘs ʙʏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇᴛᴇᴄᴛɪɴɢ ᴀɴᴅ ᴅᴇʟᴇᴛɪɴɢ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs.\n\n"
        "➜ [➕ Add Me to Your Group](https://t.me/YourBotUsername?startgroup=true)\n"
        "[🛠 Support Group](https://t.me/your_support_group)"
    )
    await update.message.reply_text(caption, parse_mode="Markdown")


# /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = str(datetime.now() - datetime.fromtimestamp(START_TIME)).split('.')[0]
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()
    disk = psutil.disk_usage('/').percent

    msg = (
        f"🤖 *Bot:* `{platform.node()}`\n"
        f"👤 *Owner:* `{OWNER_ID}`\n\n"
        f"🕐 *Uptime:* `{uptime}`\n"
        f"🧠 *RAM:* `{ram}%`\n"
        f"⚙️ *CPU:* `{cpu}%`\n"
        f"💽 *Disk:* `{disk}%`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ========== ADMIN / OWNER COMMANDS ==========

# /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    users, chats = get_bot_stats()
    await update.message.reply_text(f"👥 Users: `{users}`\n👥 Groups: `{chats}`", parse_mode="Markdown")

# /broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    text = update.message.text.split(None, 1)
    if len(text) < 2:
        return await update.message.reply_text("Usage: /broadcast [-user] [-pin] <message>")

    message = text[1]
    pin = "-pin" in message
    to_users = "-user" in message
    message = message.replace("-user", "").replace("-pin", "").strip()

    users, chats = get_bot_stats()
    count = 0

    if not to_users:
        for cid in chats:
            try:
                sent = await context.bot.send_message(cid, message)
                if pin:
                    await context.bot.pin_chat_message(cid, sent.message_id)
                count += 1
            except:
                pass

    if to_users:
        for uid in users:
            try:
                await context.bot.send_message(uid, message)
                count += 1
            except:
                pass

    await update.message.reply_text(f"✅ Broadcast sent to {count} recipients.")

# /gdel
async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("❌ Not authorized.")

    args = context.args
    if len(args) != 2 or args[0] not in ["add", "remove"]:
        return await update.message.reply_text("Usage:\n`/gdel add <user_id>`\n`/gdel remove <user_id>`", parse_mode="Markdown")

    user_id = int(args[1])
    if args[0] == "add":
        add_restricted_user(user_id)
        await update.message.reply_text(f"🚫 User `{user_id}` restricted.", parse_mode="Markdown")
    else:
        remove_restricted_user(user_id)
        await update.message.reply_text(f"✅ User `{user_id}` unrestricted.", parse_mode="Markdown")

# /delay
async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if context.args:
        try:
            sec = int(context.args[0])
            set_delay(chat_id, sec)
            return await update.message.reply_text(f"🕒 Delay set to `{sec}` seconds.")
        except:
            return await update.message.reply_text("❌ Invalid number.")
    await update.message.reply_text(f"⏰ Current delay: `{get_delay(chat_id)}s`", parse_mode="Markdown")

# ========== AUTO DELETE MONITOR ==========

async def monitor_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id
    chat = update.effective_chat

    if chat.type in ["group", "supergroup"]:
        restricted = get_restricted_users()
        if user_id in restricted:
            try:
                await msg.delete()
            except:
                pass

# ========== NOTIFICATIONS TO OWNER ==========

async def notify_private_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.effective_chat.type == "private":
        message = (
            f"📥 *New Start!*\n"
            f"👤 Username: @{user.username or 'N/A'}\n"
            f"🆔 ID: `{user.id}`\n"
            f"📩 Name: {user.full_name}"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode="Markdown")

async def notify_group_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                msg = (
                    f"➕ *Bot Added to Group!*\n"
                    f"🏘 Group: {chat.title}\n"
                    f"🆔 Group ID: `{chat.id}`\n"
                    f"👤 Added by: @{user.username or 'N/A'} ({user.id})"
                )
                await context.bot.send_message(chat_id=OWNER_ID, text=msg, parse_mode="Markdown")

# ========== MAIN ==========

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("delay", delay))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("gdel", gdel))

    # Notification and monitoring
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, notify_private_start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, notify_group_join))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.UpdateType.EDITED_MESSAGE, monitor_messages))

    print("🚀 Bot is running.")
    app.run_polling()
