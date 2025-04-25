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

# الآيدي مال الكروب
TARGET_CHAT_ID = -4708122757

def handle_message(update: Update, context):
    msg = update.message
    if msg.chat.type in ['private', 'group', 'supergroup']:
        chat_id = msg.chat_id
        if chat_id not in messages:
            messages[chat_id] = {}
        messages[chat_id][msg.message_id] = datetime.datetime.utcnow()
        print(f"📥 تم تخزين الرسالة: {msg.message_id} في {chat_id}")

def clean_old_messages(update=None, context=None):
    now = datetime.datetime.utcnow()
    for chat_id in list(messages):
        for msg_id in list(messages[chat_id]):
            sent_time = messages[chat_id][msg_id]
            if (now - sent_time).total_seconds() > 30:  # مؤقتاً 30 ثانية للتجربة
                print(f"🧹 محاولة حذف الرسالة {msg_id} من {chat_id}")
                try:
                    bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    messages[chat_id].pop(msg_id)
                    print(f"✅ تم حذف الرسالة {msg_id} من {chat_id}")
                except Exception as e:
                    print(f"❌ فشل حذف {msg_id} من {chat_id}: {e}")

def clean_command(update: Update, context):
    if update.effective_chat.id == TARGET_CHAT_ID:
        update.message.reply_text("🧹 جاري تنظيف الرسائل القديمة...")
        clean_old_messages()
        update.message.reply_text("✅ تم الحذف!")

# هاندلرات
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
dispatcher.add_handler(CommandHandler("clean_now", clean_command))

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/clean", methods=["GET"])
def clean_route():
    clean_old_messages()
    return "تم التنظيف اليدوي"

@app.route("/", methods=["GET"])
def home():
    return "البوت شغال 🔥"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
