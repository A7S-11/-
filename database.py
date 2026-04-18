# ==========================================
# قاعدة البيانات - database.py
# ==========================================

import sqlite3
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_connection():
    """الحصول على اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """تهيئة قاعدة البيانات"""
    conn = get_connection()
    cursor = conn.cursor()

    # جدول المستخدمين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance REAL DEFAULT 0.0,
            total_orders INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            joined_at TEXT DEFAULT (datetime('now')),
            last_seen TEXT DEFAULT (datetime('now'))
        )
    """)

    # جدول الطلبات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            smm_order_id TEXT,
            service_key TEXT NOT NULL,
            service_name TEXT NOT NULL,
            link TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # جدول الشحن
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT DEFAULT 'manual',
            note TEXT,
            admin_id INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


# ================= المستخدمين =================

def get_user(user_id: int):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return user


def create_or_update_user(user_id: int, username: str, full_name: str):
    conn = get_connection()
    conn.execute("""
        INSERT INTO users (user_id, username, full_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            full_name = excluded.full_name,
            last_seen = datetime('now')
    """, (user_id, username, full_name))
    conn.commit()
    conn.close()


def get_balance(user_id: int) -> float:
    conn = get_connection()
    row = conn.execute(
        "SELECT balance FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return round(row["balance"], 4) if row else 0.0


def update_balance(user_id: int, amount: float, operation: str = "add"):
    conn = get_connection()

    if operation == "add":
        conn.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
    elif operation == "subtract":
        conn.execute(
            "UPDATE users SET balance = MAX(0, balance - ?) WHERE user_id = ?",
            (amount, user_id)
        )
    elif operation == "set":
        conn.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (amount, user_id)
        )

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    users = conn.execute(
        "SELECT * FROM users WHERE status = 'active'"
    ).fetchall()
    conn.close()
    return users


def get_all_user_ids():
    conn = get_connection()
    rows = conn.execute(
        "SELECT user_id FROM users WHERE status = 'active'"
    ).fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


# ================= الطلبات =================

def create_order(user_id, service_key, service_name, link, quantity, amount):
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO orders (user_id, service_key, service_name, link, quantity, amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, service_key, service_name, link, quantity, amount))

    order_id = cursor.lastrowid

    conn.execute(
        "UPDATE users SET total_orders = total_orders + 1 WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()
    return order_id


def update_order(order_id, smm_order_id=None, status=None):
    conn = get_connection()

    if smm_order_id and status:
        conn.execute("""
            UPDATE orders
            SET smm_order_id = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (smm_order_id, status, order_id))
    elif status:
        conn.execute("""
            UPDATE orders
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (status, order_id))

    conn.commit()
    conn.close()


def get_user_orders(user_id, limit=5):
    conn = get_connection()
    orders = conn.execute("""
        SELECT * FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return orders


# ================= الشحن =================

def add_deposit(user_id, amount, method="manual", note=None, admin_id=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO deposits (user_id, amount, method, note, admin_id)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, method, note, admin_id))
    conn.commit()
    conn.close()


# ================= الإحصائيات =================

def get_bot_stats():
    conn = get_connection()

    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    active_users = conn.execute(
        "SELECT COUNT(*) FROM users WHERE status = 'active'"
    ).fetchone()[0]
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    completed_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE status = 'completed'"
    ).fetchone()[0]
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status = 'completed'"
    ).fetchone()[0]
    total_balance = conn.execute(
        "SELECT COALESCE(SUM(balance), 0) FROM users"
    ).fetchone()[0]

    conn.close()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "total_revenue": round(total_revenue, 2),
        "total_balance": round(total_balance, 2),
    }