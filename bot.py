import os
import psutil
import platform
import time
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from db import (
    is_logging_enabled, toggle_logging,
    save_chat, get_stats,
    set_deletion_delay, get_deletion_delay
)
from config import TOKEN, ADMIN_IDS, BOT_NAME, BOT_OWNER_USERNAME, SUPPORT_GROUP_LINK

start_time = time.time()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    save_chat(chat.id, chat.type)

    try:
        await update.message.reply_video(
            video="start_video.mp4",  # optional
            caption=f"Konnichiwa, {user.first_name}-senpai! 💖"
        )
    except:
        pass

    keyboard = [
        [InlineKeyboardButton("➕ Add Me to Your Group", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP_LINK)]
    ]

    await update.message.reply_text(
        "• ɪ'ᴍ ᴛʜᴇ ᴍᴏsᴛ ᴀᴅᴠᴀɴᴄᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴛᴇxᴛ ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʙᴏᴛ.\n"
        "• ɪ sᴀғᴇɢᴜᴀʀᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘs ʙʏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇᴛᴇᴄᴛɪɴɢ ᴀɴᴅ ᴅᴇʟᴇᴛɪɴɢ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs ᴀғᴛᴇʀ ᴀ sᴇᴛ ᴅᴇʟᴀʏ.\n\n"
        "⚙️ ǫᴇʏ ʜɪɢʜʟɪɢʜᴛs:\n"
        "• ᴅᴇʟᴀʏᴇᴅ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛɪᴏɴ sʏsᴛᴇᴍ\n"
        "• ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        "• ᴘᴇʀᴍɪᴛ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs\n"
        "• ғᴜʟʟʏ ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴛɪᴍᴇʀ\n\n"
        "➜ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.time() - start_time
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    system_info = platform.system() + " " + platform.release()

    try:
        await update.message.reply_video(
            video="ping_video.mp4",
            caption="Here’s my status, senpai~ 💫"
        )
    except:
        pass

    text = (
        f"🌸 *{BOT_NAME}* is online~\n\n"
        f"🖥 *System*: `{system_info}`\n"
        f"⏱ *Uptime*: `{int(uptime // 60)} min`\n"
        f"🧠 *RAM*: `{mem}%`\n"
        f"💽 *Disk*: `{disk}%`\n"
        f"🧮 *CPU*: `{cpu}%`\n\n"
        f"👤 *Owner*: @{BOT_OWNER_USERNAME}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def toggle_logging(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("Only my master can toggle logging, nya~ 😼")
        return

    new_status = toggle_logging(chat.id)
    await update.message.reply_text(f"Logging has been {'enabled' if new_status else 'disabled'}~ 💖")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("Only my master can see this, nya~ 😼")
        return

    groups, users = get_stats()
    try:
        await update.message.reply_photo(
            photo="stats_image.jpg",
            caption="Here's your bot activity snapshot, master~ 💌"
        )
    except:
        pass

    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"👥 Groups: `{groups}`\n"
        f"🙋‍♂️ Users: `{users}`",
        parse_mode="Markdown"
    )


async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if len(context.args) == 0:
        delay = get_deletion_delay(chat.id)
        await update.message.reply_text(f"⏱ Current deletion delay is *{delay} seconds*", parse_mode="Markdown")
        return

    if user.id not in ADMIN_IDS:
        await update.message.reply_text("Only my master can change the delay! 😿")
        return

    try:
        delay_val = int(context.args[0])
        if delay_val < 0 or delay_val > 300:
            raise ValueError("Out of range")
        set_deletion_delay(chat.id, delay_val)
        await update.message.reply_text(f"⏱ Delay updated to *{delay_val} seconds*", parse_mode="Markdown")
    except:
        await update.message.reply_text("Please enter a valid delay (0–300 seconds). 😅")


async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not is_logging_enabled(chat.id):
        return

    edited = update.edited_message
    if edited and edited.text:
        delay = get_deletion_delay(chat.id)
        sent = await context.bot.send_message(
            chat_id=chat.id,
            text=f"✏️ *Edited Message Detected!*\n\n"
                 f"👤 User: `{edited.from_user.first_name}`\n"
                 f"🕒 Time: `{edited.date}`\n"
                 f"💬 Message: `{edited.text}`",
            parse_mode="Markdown"
        )
        await asyncio.sleep(delay)
        await edited.delete()
        await sent.delete()


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("togglelogging", toggle_logging))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("delay", delay))
    app.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED_MESSAGE, handle_edit))

    print(f"{BOT_NAME} is now running~ 💮")
    app.run_polling()


if __name__ == "__main__":
    main()
