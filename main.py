import logging
import os
import datetime
from flask import Flask, request
from telegram import Bot, Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import Defaults
from telegram.error import TelegramError

# تفعيل الـ Debug logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")  # خلي التوكن بمتغير البيئة
GROUP_ID = -1000000000000       # حط هنا الـ Chat ID مالت الكروب

app = Flask(__name__)
bot = Bot(token=TOKEN)

defaults = Defaults(parse_mode=constants.ParseMode.HTML)
application = Application.builder().token(TOKEN).defaults(defaults).build()


async def clean_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🔄 جاري حذف الرسائل القديمة...")

        limit_sec = 3600  # افتراضي ساعة
        if context.args:
            try:
                limit_sec = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ رقم غير صالح.")
                return

        now = datetime.datetime.utcnow()
        from_id = update.effective_chat.id

        # جلب آخر 100 رسالة
        history = await bot.get_chat_history(chat_id=from_id, limit=100)

        deleted = 0
        for msg in history:
            msg_age = (now - msg.date).total_seconds()
            if msg_age > limit_sec:
                try:
                    await bot.delete_message(chat_id=from_id, message_id=msg.message_id)
                    deleted += 1
                except TelegramError as e:
                    logger.warning(f"خطأ بالحذف: {e}")

        await update.message.reply_text(f"✅ تم الحذف: {deleted} رسالة")

    except Exception as e:
        logger.error(f"فشل بالحذف: {e}")
        await update.message.reply_text("❌ فشل بالحذف")


# أمر إختبار بسيط
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أنا شغّال ✅")


# ربط الأوامر
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("clean_now", clean_now))


@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.update_queue.put(update)
    return "ok", 200
