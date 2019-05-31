

async def test_server_working(cli):
    resp = await cli.post('/register', json={'value': 'foo'})
    print(await resp.text())
    assert resp.status
