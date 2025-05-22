import asyncio
import logging
import os
import nest_asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ChatMemberHandler
)

from db import (
    add_group_if_not_exists,
    is_group_exist,
    get_edit_delay,
    set_edit_delay,
    is_user_banned,
    add_user_if_not_exists,
    get_all_groups,
    get_all_users,
    ban_user,
    unban_user,
    log_broadcast,
)


TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DELETION_DELAY = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm EditGuardian Bot.\nI'll delete edited messages from users.")
    await add_user(update.effective_user.id)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")


async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    logs = await get_logs()
    await update.message.reply_text("\n".join(logs[-10:]) or "No logs yet.")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    users = await get_all_users()
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
            count += 1
        except Exception:
            continue
    await update.message.reply_text(f"✅ Sent to {count} users.")


async def gdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message to delete it.")
        return
    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(f"Failed to delete: {e}")


async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /delay <chat_id> <seconds>")
        return
    chat_id = context.args[0]
    try:
        delay = int(context.args[1])
        await set_group_delay(chat_id, delay)
        await update.message.reply_text(f"✅ Delay for {chat_id} set to {delay} seconds.")
    except ValueError:
        await update.message.reply_text("Invalid delay value.")


async def edited(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.edited_message.chat_id)
    delay = await get_group_delay(chat_id) or DELETION_DELAY
    await asyncio.sleep(delay)
    try:
        await update.edited_message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete edited message: {e}")
    await log_message(f"Deleted edited msg from {chat_id}")


async def joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.chat_member.chat
    await add_group_if_not_exists(str(chat.id))
    logger.info(f"Joined group: {chat.title} ({chat.id})")


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("gdel", gdel))
    app.add_handler(CommandHandler("delay", delay))

    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited))
    app.add_handler(ChatMemberHandler(joined, ChatMemberHandler.MY_CHAT_MEMBER))

    await app.run_polling()


# Heroku fix for running event loop
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
