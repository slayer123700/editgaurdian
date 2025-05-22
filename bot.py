import os
import psutil
import platform
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from db import is_logging_enabled, toggle_logging, save_chat, get_stats
from config import TOKEN, ADMIN_IDS, BOT_NAME, BOT_OWNER_USERNAME, SUPPORT_GROUP_LINK

start_time = time.time()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    save_chat(chat.id, chat.type)  # Track all chats in MongoDB

    # 🌸 Optional: Send start video
    try:
        await update.message.reply_video(
            video="start_video.mp4",  # Replace with your file or URL
            caption=f"Konnichiwa, {user.first_name}-senpai!~ 💖",
        )
    except Exception as e:
        print("Start video error:", e)

    keyboard = [
        [InlineKeyboardButton("➕ Add Me to Your Group", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP_LINK)]
    ]
    await update.message.reply_text(
        f"I'm *{BOT_NAME}*, your cute little edit guardian bot~ 🍥\n"
        f"I'll watch for edited messages and protect your chat! ✨\n\n"
        f"Use /togglelogging to enable/disable logging in your group.\n"
        f"Use /ping to see my system stats!\n",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.time() - start_time
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    system_info = platform.system() + " " + platform.release()

    # 🎥 Optional: Ping video
    try:
        await update.message.reply_video(
            video="ping_video.mp4",  # Replace with your file or URL
            caption="Here’s my status, senpai~ 💫"
        )
    except Exception as e:
        print("Ping video error:", e)

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
        await update.message.reply_text("Gomenasai~ 😿 Only my master(s) can do this!")
        return

    new_status = toggle_logging(chat.id)
    status_text = "enabled~ 💖" if new_status else "disabled~ 😿"
    await update.message.reply_text(f"Logging has been {status_text}", parse_mode="Markdown")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("Only my master can see this, nya~ 😼")
        return

    groups, users = get_stats()

    # 🖼 Optional: Stats image
    try:
        await update.message.reply_photo(
            photo="stats_image.jpg",  # Replace with your file or URL
            caption="Here's your bot activity snapshot, master~ 💌"
        )
    except Exception as e:
        print("Stats image error:", e)

    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"👥 Groups: `{groups}`\n"
        f"🙋‍♂️ Users: `{users}`",
        parse_mode="Markdown"
    )


async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not is_logging_enabled(chat.id):
        return

    edited = update.edited_message
    if edited and edited.text:
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"✏️ *Edited Message Detected!*\n\n"
                 f"👤 User: `{edited.from_user.first_name}`\n"
                 f"🕒 Time: `{edited.date}`\n"
                 f"💬 Message: `{edited.text}`",
            parse_mode="Markdown"
        )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("togglelogging", toggle_logging))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED_MESSAGE, handle_edit))

    print(f"{BOT_NAME} is live~ 💮")
    app.run_polling()


if __name__ == "__main__":
    main()
