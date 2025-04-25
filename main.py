from flask import Flask, request
from telegram import Bot
from telegram.ext import Dispatcher, MessageHandler, Filters
import os
import datetime

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot, None, workers=0)
messages = {}

def handle_message(update, context):
    msg = update.message
    if msg.chat.type in ['group', 'supergroup']:
        messages[msg.message_id] = {
            'chat_id': msg.chat_id,
            'timestamp': datetime.datetime.utcnow()
        }

dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    dispatcher.process_update(bot._parse_webhook_data(update))
    return "ok"

@app.route("/clean", methods=["GET"])
def clean():
    now = datetime.datetime.utcnow()
    to_delete = []
    for msg_id, data in messages.items():
        if (now - data['timestamp']).total_seconds() > 3600:
            try:
                bot.delete_message(chat_id=data['chat_id'], message_id=msg_id)
                to_delete.append(msg_id)
            except Exception as e:
                print("Delete failed:", e)
    for msg_id in to_delete:
        messages.pop(msg_id)
    return "Cleanup done"

@app.route("/", methods=["GET"])
def home():
    return "Bot is live!"

if __name__ == "__main__":
    app.run()
