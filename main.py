import telebot
from flask import Flask, request, abort
import config
import database as db
from smm_api import smm_api
from helpers import bot, check_subscription, safe_send
import keyboards as kb

app = Flask(__name__)

@app.route(config.WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    abort(403)

@app.route("/")
def index():
    return "Bot running"

@bot.message_handler(commands=["start"])
def start(message):
    if not check_subscription(message.from_user.id):
        safe_send(message.chat.id, "اشترك أولاً", reply_markup=kb.join_channel_kb())
        return

    safe_send(message.chat.id, "اهلاً بك", reply_markup=kb.main_menu_kb())

@bot.message_handler(func=lambda m: m.text and "tiktok.com" in m.text)
def handle_link(message):
    result = smm_api.create_order(20, message.text, 1000)

    if "order" in result:
        safe_send(message.chat.id, f"✅ تم الطلب\nID: {result['order']}")
    else:
        safe_send(message.chat.id, "❌ فشل الطلب")

if __name__ == "__main__":
    db.init_db()
    bot.remove_webhook()
    bot.set_webhook(url=config.WEBHOOK_URL)
    app.run(host="0.0.0.0", port=8080)