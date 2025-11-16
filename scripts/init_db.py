# scripts/init_db.py

import asyncio
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.models.database import init_db

async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main())
