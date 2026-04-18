# ==========================================
# main.py
# ==========================================

import logging
import traceback
import threading
import time
from flask import Flask, request, abort

import telebot
from telebot.types import Message, CallbackQuery

import database as db
import keyboards as kb
from smm_api import smm_api, translate_status
from helpers import (
    bot, escape_md, is_admin, check_subscription,
    calculate_order_cost, safe_send, safe_edit
)
from config import (
    WEBHOOK_URL, WEBHOOK_PATH, FLASK_HOST, FLASK_PORT,
    SMM_SERVICES, MESSAGES
)

# ================= Logging =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ================= Flask =================
app = Flask(__name__)
user_states = {}

# ================= Webhook =================
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return abort(403)

@app.route("/")
def index():
    return "Bot Running", 200

# ================= Helpers =================
def get_or_create_user(message: Message):
    db.create_or_update_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or ""
    )

def send_main_menu(user_id):
    user = db.get_user(user_id)
    balance = user["balance"] if user else 0

    text = f"👋 أهلاً\n💰 رصيدك: {balance}$"
    safe_send(user_id, text, reply_markup=kb.main_menu_kb())

# ================= Commands =================
@bot.message_handler(commands=["start"])
def start(message):
    get_or_create_user(message)

    if not check_subscription(message.from_user.id):
        safe_send(
            message.chat.id,
            MESSAGES["not_subscribed"],
            reply_markup=kb.join_channel_kb()
        )
        return

    send_main_menu(message.chat.id)

# ================= Messages =================
@bot.message_handler(func=lambda m: m.text and "tiktok.com" in m.text)
def handle_link(message):
    user_id = message.from_user.id

    svc = list(SMM_SERVICES.values())[0]

    cost = calculate_order_cost(svc["price_per_1000"], 1000)
    balance = db.get_balance(user_id)

    if balance < cost:
        safe_send(user_id, "❌ رصيدك غير كافي")
        return

    safe_send(user_id, "⏳ جاري تنفيذ الطلب...")

    threading.Thread(
        target=_process_smm_order,
        args=(user_id, svc, message.text, 1000, cost),
        daemon=True
    ).start()

# ================= SMM =================
def _process_smm_order(user_id, svc, link, qty, cost):
    try:
        result = smm_api.create_order(svc["id"], link, qty)

        if "error" in result:
            safe_send(user_id, f"❌ فشل: {result['error']}")
            return

        db.update_balance(user_id, cost, "subtract")

        safe_send(
            user_id,
            f"✅ تم الطلب\n🆔 {result.get('order')}"
        )

    except Exception as e:
        logger.error(traceback.format_exc())
        safe_send(user_id, "❌ خطأ غير متوقع")

# ================= Fallback =================
@bot.message_handler(func=lambda m: True)
def fallback(message):
    safe_send(message.chat.id, "❓ استخدم الأزرار")

# ================= Webhook Setup =================
def setup_webhook():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    logger.info("Webhook set")

# ================= Run =================
if __name__ == "__main__":
    logger.info("Starting bot...")
    db.init_db()
    setup_webhook()
    app.run(host=FLASK_HOST, port=FLASK_PORT)