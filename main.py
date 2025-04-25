from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import os
import datetime

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# نخزن الرسائل حسب الـ chat_id
messages = {}

# الشات آيدي الخاص بالمجموعة
TARGET_CHAT_ID = -4708122757

def handle_message(update: Update, context):
    msg = update.message
    if msg.chat.type in ['private', 'group', 'supergroup']:
        chat_id = msg.chat_id
        if chat_id not in messages:
            messages[chat_id] = {}
        messages[chat_id][msg.message_id] = datetime.datetime.utcnow()

def clean_old_messages(update=None, context=None):
    now = datetime.datetime.utcnow()
    for chat_id in list(messages):
        for msg_id in list(messages[chat_id]):
            sent_time = messages[chat_id][msg_id]
            # للتجربة: نحذف بعد 30 ثانية، غيرها لـ 3600 للساعة
            if (now - sent_time).total_seconds() > 30:
                try:
                    bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    messages[chat_id].pop(msg_id)
                except Exception as e:
                    print(f"❌ Failed to delete message {msg_id} in {chat_id}: {e}")

def clean_command(update: Update, context):
    if update.effective_chat.id == TARGET_CHAT_ID:
        update.message.reply_text("🧹 جاري تنظيف الرسائل القديمة...")
        clean_old_messages()
        update.message.reply_text("✅ تم الحذف!")

# إضافة الهاندلرات
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
dispatcher.add_handler(CommandHandler("clean_now", clean_command))

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/clean", methods=["GET"])
def clean_route():
    clean_old_messages()
    return "Manual clean done"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run()
