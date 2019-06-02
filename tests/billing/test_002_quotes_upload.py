import pytest
from datetime import datetime

from decimal import Decimal, ROUND_DOWN

from app.billing.currency_convertor import CurrencyConverter


@pytest.mark.quote
async def test_load_quotes(cli):
    resp = await cli.post('/quotes_upload', json={
        'date': '2015-12-12',
        'quote': '1.890123123',
        'currency': 'CAD'
    })
    assert resp.status == 400
    resp = await cli.post('/quotes_upload', json={
        'date': '2015-12-12',
        'quote': '1.890212',
        'currency': 'CAD'
    })
    assert resp.status < 400, await resp.json()

    resp = await cli.post('/quotes_upload', json={
        'date': '2015-12-12',
        'quote': '1.890344',
        'currency': 'CAD'
    })
    assert resp.status < 400

    resp = await cli.post('/quotes_upload', json={
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'quote': '0.740627',
        'currency': 'CAD'
    })
    assert resp.status < 400

    resp = await cli.post('/quotes_upload', json={
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'quote': '0.144888',
        'currency': 'CNY'
    })
    assert resp.status < 400


@pytest.mark.converter
async def test_converter(cli):
    resp = await cli.post('/quotes_upload', json={
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'quote': '0.740627',
        'currency': 'CAD'
    })
    assert resp.status < 400

    resp = await cli.post('/quotes_upload', json={
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'quote': '0.144888',
        'currency': 'CNY'
    })
    assert resp.status < 400
    conv = CurrencyConverter(cli.app['redis'])
    assert await conv.convert(100, 'CNY', 'CAD') == Decimal('19.56').quantize(Decimal('.01'), rounding=ROUND_DOWN)
