BOT_TOKEN = "PUT_YOUR_TOKEN"
ADMIN_ID = 123456789
CHANNEL_ID = "@your_channel"

WEBHOOK_HOST = "https://your-app.up.railway.app"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 8080

DATABASE_PATH = "smm_bot.db"

SMM_API_URL = "https://your-smm-panel.com/api/v2"
SMM_API_KEY = "PUT_YOUR_KEY"

SMM_SERVICES = {
    "tiktok_views": {
        "id": 20,
        "name": "مشاهدات تيك توك",
        "price_per_1000": 0.1,
        "min": 100,
        "max": 100000,
        "emoji": "🎵"
    }
}

MESSAGES = {
    "not_subscribed": "⚠️ اشترك أولاً",
    "support": "👨‍💻 @your_username"
}