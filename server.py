from aiohttp import web

from app.billing.models import init_db
from app.billing.views import register, make_deposit, money_transfer, quotes_upload, report


def setup_routes(app):
    app.router.add_post('/register', register)
    app.router.add_post('/make_deposit', make_deposit)
    app.router.add_post('/money_transfer', money_transfer)
    app.router.add_post('/quotes_upload', quotes_upload)
    app.router.add_post('/report', report)


def make_app():
    app = web.Application(debug=True)
    app['config'] = {}
    setup_routes(app)
    init_db(app)
    return app


if __name__ == "__main__":
    web.run_app(make_app())
