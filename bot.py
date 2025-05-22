import time
import os
import platform
import psutil
from datetime import datetime
from telegram import Update, ChatMemberUpdated
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ChatMemberHandler,
)
from config import BOT_TOKEN, OWNER_ID, BOT_NAME, OWNER_USERNAME
from db import (
    add_user,
    add_group,
    is_restricted,
    add_restricted_user,
    get_all_users,
    get_all_chats,
    get_edit_delay,
    set_edit_delay,
)

start_time = time.time()


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)
    try:
        with open("media/start.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo,
                caption=(
                    f"👋 ʜᴇʏ {user.mention_html()},\n\n"
                    "• ɪ'ᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴛᴇxᴛ ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʙᴏᴛ.\n"
                    "• ɪ sᴀғᴇɢᴜᴀʀᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘs ʙʏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇᴛᴇᴄᴛɪɴɢ ᴀɴᴅ ᴅᴇʟᴇᴛɪɴɢ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs ᴀғᴛᴇʀ ᴀ sᴇᴛ ᴅᴇʟᴀʏ.\n\n"
                    "⚙️ ǫᴇʏ ʜɪɢʜʟɪɢʜᴛs:\n"
                    "• ᴅᴇʟᴀʏᴇᴅ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛɪᴏɴ\n"
                    "• ᴘᴇʀᴍɪᴛ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs\n"
                    "• ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
                    "➜ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ."
                ),
                parse_mode="HTML"
            )
    except:
        await update.message.reply_text("Welcome! Media missing. Bot is active.")


# /ping command
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = str(datetime.now() - datetime.fromtimestamp(start_time)).split('.')[0]
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    try:
        with open("media/ping.mp4", "rb") as video:
            await update.message.reply_video(
                video,
                caption=(
                    f"🤖 <b>{BOT_NAME}</b>\n\n"
                    f"📡 <b>Uptime:</b> {uptime}\n"
                    f"🖥 <b>CPU:</b> {cpu}%\n"
                    f"💾 <b>RAM:</b> {ram}%\n"
                    f"💽 <b>Disk:</b> {disk}%\n\n"
                    f"👤 <b>Owner:</b> @{OWNER_USERNAME}"
                ),
                parse_mode="HTML"
            )
    except:
        await update.message.reply_text(
            f"{BOT_NAME} is online!\nUptime: {uptime}"
        )


# /delay command
async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    delay = get_edit_delay(chat_id)
    await update.message.reply_text(f"✏️ Current edit deletion delay: {delay} seconds.")


# /stats command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    users = len(get_all_users())
    groups = len(get_all_chats())
    try:
        with open("media/stats.jpg", "rb") as img:
            await update.message.reply_photo(
                img,
                caption=f"📊 Stats\n\n👥 Users: {users}\n👥 Groups: {groups}",
            )
    except:
        await update.message.reply_text(f"Users: {users}, Groups: {groups}")


# /logs command
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("Logs not implemented.")


# /broadcast command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text.split(maxsplit=1)
    if len(text) < 2:
        return await update.message.reply_text("Usage: /broadcast [-user] [-pin] <message>")

    flags = text[0]
    message = text[1]

    users = get_all_users() if "-user" in flags else []
    groups = get_all_chats()

    for cid in users + groups:
        try:
            sent = await context.bot.send_message(cid, message)
            if "-pin" in flags:
                await sent.pin()
        except:
            continue

    await update.message.reply_text("Broadcast sent.")


# /gdel command
async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /gdel <user_id>")

    try:
        user_id = int(context.args[0])
        add_restricted_user(user_id)
        await update.message.reply_text(f"User {user_id} added to restricted list.")
    except:
        await update.message.reply_text("Invalid user ID.")


# edited message handler
async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.edited_message
    if not msg or not msg.text:
        return

    chat_id = msg.chat.id
    delay = get_edit_delay(chat_id)

    await context.bot.send_message(chat_id, "✏️ Edited message detected. Will be deleted soon.", reply_to_message_id=msg.message_id)
    await asyncio.sleep(delay)
    await msg.delete()


# restricted user message deletion
async def monitor_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_restricted(update.effective_user.id):
        try:
            await update.message.delete()
        except:
            pass


# bot join or user start alert
async def joined(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
    if update.my_chat_member.new_chat_member.status == "member":
        chat = update.effective_chat
        add_group(chat.id)
        await context.bot.send_message(OWNER_ID, f"Bot added to group: {chat.title} ({chat.id})")


async def started(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        user = update.effective_user
        add_user(user.id)
        await context.bot.send_message(OWNER_ID, f"User started bot: @{user.username} ({user.id})")


# Main function
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("gdel", gdel))
    app.add_handler(CommandHandler("delay", delay))

    app.add_handler(MessageHandler(filters.ALL, monitor_message))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edit))
    app.add_handler(ChatMemberHandler(joined, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, started))

    await app.run_polling()

import asyncio

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()



