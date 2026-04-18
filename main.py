import asyncio
import re
import os
import json
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite
from asyncio import Queue

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

TIKTOK_REGEX = r"https?://(www\.)?tiktok\.com/.*"
DB_PATH = "system.db"

# Queue بدل Redis
task_queue = Queue()

# --- DB ---
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            link TEXT,
            status TEXT,
            retries INTEGER DEFAULT 0
        )
        """)
        await db.commit()

async def add_order(user_id, link):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, link, status) VALUES (?, ?, ?)",
            (user_id, link, "pending")
        )
        await db.commit()
        return cursor.lastrowid

async def update_status(order_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id)
        )
        await db.commit()

# --- Handlers ---
@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("👋 أرسل رابط TikTok")

@dp.message()
async def handle(msg: Message):
    if not re.match(TIKTOK_REGEX, msg.text or ""):
        return

    order_id = await add_order(msg.from_user.id, msg.text)

    await task_queue.put({
        "order_id": order_id,
        "user_id": msg.from_user.id,
        "link": msg.text
    })

    await msg.answer(f"📥 تم تسجيل طلبك #{order_id}")

# --- Worker ---
async def worker():
    while True:
        task = await task_queue.get()

        order_id = task["order_id"]
        user_id = task["user_id"]

        try:
            await update_status(order_id, "processing")
            await asyncio.sleep(3)  # تنفيذ وهمي

            await update_status(order_id, "completed")
            await bot.send_message(user_id, f"✅ تم تنفيذ الطلب #{order_id}")

        except Exception:
            await update_status(order_id, "failed")

        task_queue.task_done()

# --- تشغيل ---
async def main():
    await init_db()

    for _ in range(2):
        asyncio.create_task(worker())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
