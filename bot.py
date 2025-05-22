import logging
import time
import psutil
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import TOKEN, ADMIN_IDS, BOT_NAME, BOT_OWNER_USERNAME, SUPPORT_GROUP_LINK

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

edit_log_enabled = {}
START_TIME = time.time()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = context.bot.username
    if update.effective_chat.type != "private":
        return

    message = (
        f"🎀 *Hiya senpai~!* I'm *{BOT_NAME}*, your adorable message guardian angel~ 💌\n\n"
        "I’ll help you watch over edited messages in your group chats~ 🍡\n\n"
        "*✨ Here’s what I can do:*\n"
        "`/start` - Show this message\n"
        "`/ping` - Check my health and uptime status 🌸\n"
        "`/togglelogging` - Enable/disable edit logging (admin only~)\n\n"
        "Add me to a group so I can start helping you~ 💮\n\n"
        "Need help? Join my Support Group below~ ☁️"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Edit-chan to your group 💮", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("🧸 Join Support Group ☁️", url=SUPPORT_GROUP_LINK)]
    ])

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=keyboard)

async def toggle_logging(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Hauu~ you're not allowed to touch that, nya~ 😿")
        return

    enabled = edit_log_enabled.get(chat_id, False)
    edit_log_enabled[chat_id] = not enabled
    status = "enabled~ 💕" if not enabled else "disabled~ 😿"
    await update.message.reply_text(f"Okay senpai! Logging is now *{status}*", parse_mode="Markdown")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(int(time.time() - START_TIME)))
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    text = (
        f"🎀 *{BOT_NAME} is online!*\n\n"
        f"🧑‍💻 *Master:* @{BOT_OWNER_USERNAME}\n\n"
        f"⏳ *Uptime:* `{uptime}`\n"
        f"🧠 *CPU-chan:* `{cpu}%` working hard~\n"
        f"📦 *RAM-chan:* `{memory}%` full of data~\n"
        f"🗂 *Disk-chan:* `{disk}%` storage safe and sound~\n\n"
        f"Thank you for taking care of me, senpai~ 💖"
    )

    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.edited_message
    chat_id = message.chat.id

    if not edit_log_enabled.get(chat_id, False):
        return

    original = message.text or "[non-text message]"
    edited = message.text or "[non-text message]"
    await message.reply_text(f"✨ Edit detected~!\nOld: `{original}`\nNew: `{edited}`", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("togglelogging", toggle_logging))
    app.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED, handle_edit))
    app.run_polling()

if __name__ == '__main__':
    main()
