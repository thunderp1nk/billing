import sys

import pytest

import settings
from db import create_tables, drop_tables
from app.billing.models import db

from server import make_app


sys.path.append("..")


@pytest.fixture(autouse=True, scope="function")
def app_configure(loop):
    db_url = settings.DB_URL
    loop.run_until_complete(db.set_bind(db_url))
    loop.run_until_complete(drop_tables(db))
    loop.run_until_complete(create_tables(db))
    yield


@pytest.fixture
def cli(loop, aiohttp_client):
    app = loop.run_until_complete(make_app(debug_mode=True))
    return loop.run_until_complete(aiohttp_client(app))
