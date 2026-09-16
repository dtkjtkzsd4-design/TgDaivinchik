import aiosqlite
from datetime import datetime

from config import DB_PATH

ALLOWED_FIELDS = {
    "name", "age", "gender", "looking_for", "city", "about",
    "photo_id", "search_mode", "min_age", "max_age", "is_active", "username",
}


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                age INTEGER,
                gender TEXT,
                looking_for TEXT,
                city TEXT,
                about TEXT,
                photo_id TEXT,
                search_mode TEXT DEFAULT 'city',
                min_age INTEGER DEFAULT 18,
                max_age INTEGER DEFAULT 99,
                is_active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user INTEGER,
                to_user INTEGER,
                action TEXT,
                created_at TEXT,
                UNIQUE(from_user, to_user)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1 INTEGER,
                user2 INTEGER,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user INTEGER,
                to_user INTEGER,
                created_at TEXT
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def create_user(user_id, username, name, age, gender, looking_for, city, about, photo_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users
            (user_id, username, name, age, gender, looking_for, city, about, photo_id,
             search_mode, min_age, max_age, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'city', 18, 99, 1, ?)
        """, (user_id, username, name, age, gender, looking_for, city, about, photo_id,
              datetime.utcnow().isoformat()))
        await db.commit()


async def update_field(user_id: int, field: str, value):
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"Field not allowed: {field}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()


async def deactivate_user(user_id: int):
    await update_field(user_id, "is_active", 0)


async def get_next_profile(user_id: int):
    """Возвращает следующую подходящую анкету, которую user_id ещё не оценивал."""
    user = await get_user(user_id)
    if not user:
        return None

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
            SELECT * FROM users
            WHERE user_id != ?
              AND is_active = 1
              AND user_id NOT IN (SELECT to_user FROM likes WHERE from_user = ?)
              AND user_id NOT IN (SELECT to_user FROM blocks WHERE from_user = ?)
              AND user_id NOT IN (SELECT from_user FROM blocks WHERE to_user = ?)
              AND age BETWEEN ? AND ?
        """
        params = [user_id, user_id, user_id, user_id, user["min_age"], user["max_age"]]

        if user["looking_for"] != "any":
            query += " AND gender = ?"
            params.append(user["looking_for"])

        query += " AND (looking_for = 'any' OR looking_for = ?)"
        params.append(user["gender"])

        if user["search_mode"] == "city":
            query += " AND city = ?"
            params.append(user["city"])

        query += " ORDER BY RANDOM() LIMIT 1"

        cur = await db.execute(query, params)
        row = await cur.fetchone()
        return dict(row) if row else None


async def add_like(from_user: int, to_user: int, action: str) -> bool:
    """Сохраняет лайк/дизлайк. Возвращает True, если образовался взаимный мэтч."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO likes (from_user, to_user, action, created_at)
            VALUES (?, ?, ?, ?)
        """, (from_user, to_user, action, datetime.utcnow().isoformat()))
        await db.commit()

        if action != "like":
            return False

        cur = await db.execute(
            "SELECT 1 FROM likes WHERE from_user = ? AND to_user = ? AND action = 'like'",
            (to_user, from_user),
        )
        mutual = await cur.fetchone()
        if mutual:
            await db.execute(
                "INSERT INTO matches (user1, user2, created_at) VALUES (?, ?, ?)",
                (from_user, to_user, datetime.utcnow().isoformat()),
            )
            await db.commit()
            return True
        return False


async def get_pending_likes(user_id: int):
    """Анкеты тех, кто лайкнул user_id, а user_id ещё не ответил лайком/дизлайком."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT u.* FROM users u
            JOIN likes l ON l.from_user = u.user_id
            WHERE l.to_user = ? AND l.action = 'like'
              AND u.is_active = 1
              AND u.user_id NOT IN (SELECT to_user FROM likes WHERE from_user = ?)
            ORDER BY l.created_at DESC
        """, (user_id, user_id))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def add_block(from_user: int, to_user: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO blocks (from_user, to_user, created_at) VALUES (?, ?, ?)",
            (from_user, to_user, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def get_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM likes WHERE to_user = ? AND action = 'like'", (user_id,)
        )
        likes_received = (await cur.fetchone())[0]
        cur = await db.execute(
            "SELECT COUNT(*) FROM matches WHERE user1 = ? OR user2 = ?", (user_id, user_id)
        )
        matches = (await cur.fetchone())[0]
        return {"likes_received": likes_received, "matches": matches}
