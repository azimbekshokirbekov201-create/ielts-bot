import aiosqlite

DB_PATH = "ielts_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                full_name TEXT,
                username TEXT,
                is_premium INTEGER DEFAULT 0,
                writing_count INTEGER DEFAULT 0,
                quiz_score INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS writing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                topic TEXT,
                essay TEXT,
                feedback TEXT,
                band_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                question TEXT,
                user_answer TEXT,
                correct_answer TEXT,
                is_correct INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_user(telegram_id: int, full_name: str, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (telegram_id, full_name, username)
            VALUES (?, ?, ?)
        """, (telegram_id, full_name, username))
        await db.commit()

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()

async def is_premium(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT is_premium FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0])

async def set_premium(telegram_id: int, status: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_premium = ? WHERE telegram_id = ?",
            (status, telegram_id)
        )
        await db.commit()

async def save_writing(telegram_id: int, topic: str, essay: str, feedback: str, band_score: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO writing_history (telegram_id, topic, essay, feedback, band_score)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, topic, essay, feedback, band_score))
        await db.execute(
            "UPDATE users SET writing_count = writing_count + 1 WHERE telegram_id = ?",
            (telegram_id,)
        )
        await db.commit()

async def get_writing_history(telegram_id: int, limit: int = 5):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT topic, band_score, created_at FROM writing_history
            WHERE telegram_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (telegram_id, limit)) as cursor:
            return await cursor.fetchall()

async def get_stats(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT writing_count, quiz_score, is_premium FROM users
            WHERE telegram_id = ?
        """, (telegram_id,)) as cursor:
            return await cursor.fetchone()
