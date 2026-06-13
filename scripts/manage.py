#!/usr/bin/env python
import asyncio
import argparse
from src.core.database import async_session
from src.core.user_engine import User

async def promote_user(telegram_id: int, role: str):
    async with async_session() as db:
        user = await db.get(User, telegram_id=telegram_id)
        if user:
            user.role = role
            await db.commit()
            print(f"User {telegram_id} promoted to {role}")
        else:
            print("User not found")

def main():
    parser = argparse.ArgumentParser(description="TEOS Management CLI")
    parser.add_argument("--promote", nargs=2, metavar=("TELEGRAM_ID", "ROLE"))
    args = parser.parse_args()
    if args.promote:
        tg_id, role = int(args.promote[0]), args.promote[1]
        asyncio.run(promote_user(tg_id, role))

if __name__ == "__main__":
    main()
