from datetime import datetime

from aiohttp import web
from decimal import Decimal

from app.billing.service_layers import Register, QuotesUpload, MakeDeposit, MoneyTransfer, Report
from app.billing.types import CurrencyType, AllCurrencyType
from app.utils import check_required_args


async def register(request):
    json_response = await request.json()
    try:
        check_required_args(json_response, Register)
        await Register(
            name=json_response['name'],
            city=json_response['city'],
            country=json_response['country'],
            currency=AllCurrencyType(json_response['currency']),
        ).execute(request['connection'])
    except Exception:
        return web.Response(status=400)
    return web.json_response(status=201)


async def make_deposit(request):
    json_response = await request.json()

    try:
        check_required_args(json_response, MakeDeposit)
        await MakeDeposit(
            user_id=json_response['user_id'],
            currency=AllCurrencyType(json_response['currency']),
            value=Decimal(json_response['value']),
        ).execute(request['connection'])
    except Exception:
        return web.Response(status=400)
    return web.json_response(status=201)


async def money_transfer(request):
    json_response = await request.json()

    try:
        check_required_args(json_response, MoneyTransfer)
        await MoneyTransfer(
            sender_user_id=json_response['sender_user_id'],
            sender_currency=AllCurrencyType(json_response['sender_currency']),
            sender_value=Decimal(json_response['sender_value']),
            recipient_user_id=json_response['recipient_user_id'],
        ).execute(request['connection'])
    except Exception:
        return web.Response(status=400)
    return web.json_response(status=201)


async def quotes_upload(request):
    json_response = await request.json()

    try:
        check_required_args(json_response, QuotesUpload)
        await QuotesUpload(
            date=datetime.strptime(json_response['date'], '%Y-%m-%d'),
            currency=CurrencyType(json_response['currency']),
            quote=Decimal(json_response['quote']),
        ).execute(request['connection'])
    except Exception:
        return web.Response(status=400)
    return web.json_response(status=201)


async def report(request):
    json_response = await request.json()

    try:
        check_required_args(json_response, Report)
        await Report(
            user_name=json_response['user_name'],
            start_date=datetime.strptime(
                json_response['start_date'], '%Y-%m-%d') if json_response.get('start_date') else None,
            end_date=datetime.strptime(
                json_response['end_date'], '%Y-%m-%d') if json_response.get('end_date') else None,
        ).execute(request['connection'])
    except Exception:
        return web.Response(status=400)
    return web.json_response(status=200)
