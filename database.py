import aiosqlite

DB_NAME = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            welcome_channel INTEGER,
            log_channel INTEGER,
            welcome_message TEXT
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS economy (
            guild_id INTEGER,
            user_id INTEGER,
            balance INTEGER DEFAULT 0,
            last_daily INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS xp (
            guild_id INTEGER,
            user_id INTEGER,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )""")
        await db.commit()
