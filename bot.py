import logging
import os
import psutil
import time
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackContext
)
from config import BOT_TOKEN, OWNER_ID, BOT_NAME, OWNER_USERNAME
from db import (
    add_user, add_chat, is_user_restricted, add_restricted_user, remove_restricted_user,
    get_restricted_users, get_all_chats, get_all_users,
    set_delay, get_delay
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

start_time = time.time()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await add_user(user.id)
    text = (
        f"👋 𝐇𝐞𝐲 {user.mention_html()}!\n\n"
        "• ɪ'ᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴛᴇxᴛ ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʙᴏᴛ.\n"
        "• ɪ sᴀғᴇɢᴜᴀʀᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘs ʙʏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇᴛᴇᴄᴛɪɴɢ ᴀɴᴅ ᴅᴇʟᴇᴛɪɴɢ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs ᴀғᴛᴇʀ ᴀ sᴇᴛ ᴅᴇʟᴀʏ.\n\n"
        "⚙️ ǫᴇʏ ʜɪɢʜʟɪɢʜᴛs:\n"
        "• ᴅᴇʟᴀʏᴇᴅ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛɪᴏɴ sʏsᴛᴇᴍ\n"
        "• ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        "• ᴘᴇʀᴍɪᴛ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs\n"
        "• ғᴜʟʟʏ ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴛɪᴍᴇʀ\n\n"
        "➜ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ."
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{BOT_NAME}?startgroup=true")]])
    await update.message.reply_photo("https://placehold.co/600x400?text=Start+Image", caption=text, reply_markup=keyboard, parse_mode="HTML")

# /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.time() - start_time
    usage = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    disk = psutil.disk_usage('/')
    text = (
        f"👾 <b>{BOT_NAME} Status</b>\n"
        f"👤 Owner: {OWNER_USERNAME}\n\n"
        f"⏱ Uptime: {int(uptime)}s\n"
        f"🧠 RAM: {usage.percent}%\n"
        f"💾 Disk: {disk.percent}%\n"
        f"⚙️ CPU: {cpu}%"
    )
    await update.message.reply_photo("https://placehold.co/600x400?text=Ping+Image", caption=text, parse_mode="HTML")

# /delay
async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        group_id = update.effective_chat.id
        if context.args:
            try:
                seconds = int(context.args[0])
                await set_delay(group_id, seconds)
                await update.message.reply_text(f"🕒 Delay set to {seconds} seconds.")
            except ValueError:
                await update.message.reply_text("❗ Please enter a valid number of seconds.")
        else:
            seconds = await get_delay(group_id)
            await update.message.reply_text(f"⏱ Current delay: {seconds} seconds.")
    else:
        await update.message.reply_text("❗ This command only works in groups.")

# /broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        return await update.message.reply_text("Usage:\n/broadcast -user\n/broadcast -user -pin\n/broadcast (groups only)")
    text = update.message.text.split(None, 1)[-1]
    to_users = "-user" in context.args
    to_pin = "-pin" in context.args
    users = await get_all_users() if to_users else []
    chats = await get_all_chats()
    targets = users + chats if to_users else chats
    for chat_id in targets:
        try:
            msg = await context.bot.send_message(chat_id, text)
            if to_pin:
                await context.bot.pin_chat_message(chat_id, msg.message_id)
        except Exception:
            continue
    await update.message.reply_text("✅ Broadcast sent.")

# /gdel
async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        return await update.message.reply_text("Usage: /gdel user_id")
    user_id = int(context.args[0])
    await add_restricted_user(user_id)
    await update.message.reply_text(f"🚫 Messages from {user_id} will now be deleted.")

# /logs
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if os.path.exists("logs.txt"):
        await update.message.reply_document("logs.txt")
    else:
        await update.message.reply_text("No logs found.")

# /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    users = len(await get_all_users())
    chats = len(await get_all_chats())
    await update.message.reply_photo("https://placehold.co/600x400?text=Stats", caption=f"📊 Users: {users}\n👥 Groups: {chats}")

# Handle edits
async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.edited_message
    chat_id = msg.chat_id
    if await is_user_restricted(msg.from_user.id):
        return await msg.delete()
    delay = await get_delay(chat_id)
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass

# Handle new groups
async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_chat(update.effective_chat.id)

# Run bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("delay", delay))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("gdel", gdel))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edit))

    app.run_polling()

if __name__ == "__main__":
    import asyncio
    main()
