# ==========================================
# إعدادات البوت - config.py
# ==========================================

# — إعدادات تيليجرام —
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 123456789
CHANNEL_ID = "@your_channel"

# — إعدادات Webhook —
WEBHOOK_HOST = "https://your-app.railway.app"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# — إعدادات Flask —
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 8080  # مهم لـ Railway

# — قاعدة البيانات —
DATABASE_PATH = "smm_bot.db"

# — SMM API —
SMM_API_URL = "https://your-smm-panel.com/api/v2"
SMM_API_KEY = "YOUR_SMM_API_KEY_HERE"

# — الخدمات —
SMM_SERVICES = {
    "tiktok_views": {
        "id": 20,
        "name": "مشاهدات تيك توك",
        "price_per_1000": 0.3,
        "min": 100,
        "max": 100000,
        "emoji": "🎵"
    }
}

# — الرسائل —
MESSAGES = {
    "welcome": "👋 أهلاً بك في بوت SMM",
    "not_subscribed": "⚠️ يجب الاشتراك بالقناة أولاً",
    "support": "📩 تواصل مع الدعم: @YourSupportUsername"
}