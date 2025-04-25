import os
import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# تخزين الرسائل
messages = {}

# الكود الرئيسي للتخزين
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg and msg.chat.type in ['group', 'supergroup']:
        chat_id = msg.chat_id
        if chat_id not in messages:
            messages[chat_id] = {}

        messages[chat_id][msg.message_id] = datetime.datetime.utcnow()
        print(f"📥 [تخزين] msg_id={msg.message_id} | chat={chat_id}")

# أمر الحذف الفوري
async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("🧨 بدء حذف الرسائل...")
    await clean_all(chat_id)
    await update.message.reply_text("✅ انتهى الحذف!")

# حذف كل الرسائل المخزونة
async def clean_all(chat_id):
    if chat_id not in messages:
        print(f"⚠️ [تحذير] لا توجد رسائل مخزونة للكروب {chat_id}")
        return

    print(f"🧹 [حذف] بدء الحذف في {chat_id}")
    for msg_id in list(messages[chat_id]):
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
            print(f"✅ [تم الحذف] msg_id={msg_id} من chat={chat_id}")
        except Exception as e:
            print(f"❌ [فشل الحذف] msg_id={msg_id} | chat={chat_id} | السبب: {e}")

    messages[chat_id] = {}
    print(f"🏁 [انتهى] تم تنظيف الكروب {chat_id}")

# ربط Webhook بفلask
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    print(f"🌐 [Webhook] وصلك شي من Telegram")
    await application.update_queue.put(Update.de_json(data, bot))
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot is up and running!"

# إعداد البوت
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
application.add_handler(CommandHandler("clean_now", clean_command))

# تشغيل Flask بالتوازي مع البوت
if __name__ == "__main__":
    import threading

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    threading.Thread(target=run_flask).start()
    print("🚀 Bot is starting...")

