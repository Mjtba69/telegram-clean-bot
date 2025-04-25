import os
import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# تخزين الرسائل
messages = {}

# وقت الحذف (ثواني) – خليه 3600 للساعة
DELETE_AFTER_SECONDS = 3600

# سجل كل رسالة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg and msg.chat.type in ['private', 'group', 'supergroup']:
        chat_id = msg.chat_id
        if chat_id not in messages:
            messages[chat_id] = {}
        messages[chat_id][msg.message_id] = datetime.datetime.utcnow()
        print(f"📥 تخزين: msg {msg.message_id} in {chat_id}")

# حذف الرسائل القديمة
async def clean_old_messages():
    now = datetime.datetime.utcnow()
    for chat_id in list(messages.keys()):
        for msg_id in list(messages[chat_id]):
            sent_time = messages[chat_id][msg_id]
            if (now - sent_time).total_seconds() > DELETE_AFTER_SECONDS:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    del messages[chat_id][msg_id]
                    print(f"🗑️ حذف: msg {msg_id} from {chat_id}")
                except Exception as e:
                    print(f"⚠️ ما نقدر نحذف msg {msg_id}: {e}")

# أمر التنظيف اليدوي من الكروب
async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧹 جاري حذف الرسائل القديمة...")
    await clean_old_messages()
    await update.message.reply_text("✅ تم الحذف!")

# ربط Webhook بفلask
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    await application.update_queue.put(Update.de_json(data, bot))
    return "ok"

# GET لتنظيف خارجي
@app.route("/clean", methods=["GET"])
def clean_external():
    asyncio.run(clean_old_messages())
    return "✅ تم حذف الرسائل القديمة (خارجي)"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

# التطبيق
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
application.add_handler(CommandHandler("clean_now", clean_command))

if __name__ == "__main__":
    import threading

    # Flask run thread
    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    threading.Thread(target=run_flask).start()
    print("🚀 Bot is starting...")
    application.run_polling(stop_signals=None)
