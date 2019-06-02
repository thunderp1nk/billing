import asyncio

import aioredis
from aiohttp import web

import settings
from app.billing.models import init_db
from app.billing.views import register, make_deposit, money_transfer, quotes_upload, report


def setup_routes(app):
    app.router.add_post('/register', register)
    app.router.add_post('/make_deposit', make_deposit)
    app.router.add_post('/money_transfer', money_transfer)
    app.router.add_post('/quotes_upload', quotes_upload)
    app.router.add_post('/report', report)


async def make_app(debug_mode=False):

    async def close_redis(app):
        app['redis'].close()

    app = web.Application(debug=debug_mode)
    app['config'] = {}

    setup_routes(app)
    init_db(app)

    app['redis'] = await aioredis.create_redis(
        (settings.REDIS_HOST, settings.REDIS_PORT), db=settings.REDIS_DB, encoding='utf-8')

    app.on_shutdown.append(close_redis)
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(make_app())
    web.run_app(make_app())
