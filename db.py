import argparse
import asyncio

import settings
from app.billing.models import db


async def create_tables(gino_db):
    await gino_db.gino.create_all()


async def drop_tables(gino_db):
    await gino_db.gino.drop_all()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--create", action='store_true')
    parser.add_argument("-d", "--drop", action='store_true')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    db_url = settings.DB_URL
    loop.run_until_complete(db.set_bind(db_url))

    if args.create:
        loop.run_until_complete(create_tables(db))
    elif args.drop:
        loop.run_until_complete(drop_tables(db))
