from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_ID

def main_menu_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🚀 بدء الرشق", callback_data="smm_menu"))
    kb.add(InlineKeyboardButton("💰 محفظتي", callback_data="wallet"))
    return kb

def join_channel_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 اشترك", url=f"https://t.me/{CHANNEL_ID.replace('@','')}"))
    kb.add(InlineKeyboardButton("✅ تحقق", callback_data="check_join"))
    return kb