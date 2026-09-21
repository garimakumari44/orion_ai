import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.connect() as conn:
        r = await conn.execute(text("""
            SELECT current_database(), current_user,
                   current_schema(),
                   (SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema='public'
                      AND table_name='companies'
                      AND column_name='figi') AS figi
        """))
        print(r.fetchone())

    await engine.dispose()

asyncio.run(main())
