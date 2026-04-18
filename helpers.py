import re
import telebot
import logging
from config import BOT_TOKEN, CHANNEL_ID, ADMIN_ID

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MarkdownV2")

def escape_md(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", str(text))

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def check_subscription(user_id: int) -> bool:
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning(f"Subscription check error: {e}")
        return True

def calculate_order_cost(price_per_1000: float, quantity: int) -> float:
    return round((price_per_1000 / 1000) * quantity, 4)

def safe_send(user_id: int, text: str, **kwargs):
    try:
        return bot.send_message(user_id, text, **kwargs)
    except Exception as e:
        logger.error(f"Send error: {e}")
        return None

def safe_edit(call, text: str, **kwargs):
    try:
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            **kwargs
        )
    except:
        safe_send(call.from_user.id, text)