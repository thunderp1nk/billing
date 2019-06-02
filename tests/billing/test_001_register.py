import pytest


@pytest.mark.reg
async def test_register(cli):
    resp = await cli.post('/register', json={
        'name': 123123,
        'country': 'Cyprus',
        'city': 'Limassol',
        'currency': 'USD',
    })
    assert resp.status == 400

    resp = await cli.post('/register', json={
        'country': 'Cyprus',
        'city': 'Limassol',
        'currency': 'USD',
    })
    assert resp.status == 400

    resp = await cli.post('/register', json={
        'name': 'johndoe',
        'country': 'Cyprus',
        'city': 'Limassol',
        'currency': 'RU',
    })
    assert resp.status == 400

    resp = await cli.post('/register', json={
        'name': 'johndoe',
        'country': 'Cyprus',
        'city': 'Limassol',
        'currency': 'USD',
    })
    assert resp.status < 400

    resp = await cli.post('/register', json={
        'name': 'johndoe',
        'country': 'Cyprus',
        'city': 'Limassol',
        'currency': 'USD',
    })
    assert resp.status == 400
