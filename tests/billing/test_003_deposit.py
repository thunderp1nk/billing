import pytest
from datetime import datetime


@pytest.mark.quote
@pytest.mark.reg
async def test_make_deposit(cli):
    resp = await cli.post('/register', json={
        'name': 'johndoe',
        'country': 'Cyprus',
        'city': 'Limassol',
        'currency': 'USD',
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

    resp = await cli.post('/make_deposit', json={
        'user_id': 1,
        'value': '300',
        'currency': 'CNY'
    })
    assert resp.status < 400
