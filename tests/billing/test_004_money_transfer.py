import pytest
from datetime import datetime


@pytest.mark.transfer
async def test_money_transfer(cli):
    resp = await cli.post('/register', json={
        'name': 'johndoe',
        'country': 'Cyprus',
        'city': 'Limassol',
        'currency': 'USD',
    })
    assert resp.status < 400

    resp = await cli.post('/register', json={
        'name': 'janedoe',
        'country': 'Montenegro',
        'city': 'Budva',
        'currency': 'CAD',
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
        'value': '300.00',
        'currency': 'CNY'
    })
    assert resp.status < 400

    resp = await cli.post('/money_transfer', json={
        'sender_user_id': 1,
        'sender_value': '58.71',
        'sender_currency': 'CAD',
        'recipient_user_id': 2
    })
    assert resp.status >= 400

    resp = await cli.post('/money_transfer', json={
        'sender_user_id': 1,
        'sender_value': '58.65',
        'sender_currency': 'CAD',
        'recipient_user_id': 2
    })
    assert resp.status < 400
