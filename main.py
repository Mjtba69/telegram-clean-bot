import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# اقرأ التوكن من environment
TOKEN = os.getenv("BOT_TOKEN")

# سوي تطبيق Flask
app = Flask(__name__)

# أنشئ البوت
application = Application.builder().token(TOKEN).build()

# وظيفة أمر التنظيف
async def clean_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # راسل تأكيد بدء التنظيف
    await context.bot.send_message(chat_id, "🧹 جاري حذف الرسائل القديمة...")

    # احذف آخر 100 رسالة (ممكن تغير الرقم)
    async for msg in context.bot.get_chat_history(chat_id, limit=100):
        try:
            await context.bot.delete_message(chat_id, msg.message_id)
        except Exception as e:
            print(f"ما انحذفت الرسالة {msg.message_id}، السبب: {e}")
            continue

    # تم الحذف
    await context.bot.send_message(chat_id, "✅ تم الحذف!")

# أضف الأمر للبوت
application.add_handler(CommandHandler("clean_now", clean_now))

# نقطة استقبال webhook
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# مسار رئيسي للتأكد إن السيرفر شغال
@app.route("/")
def home():
    return "بوت التنظيف شغّال ✅", 200

# شغّل السيرفر على Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
