from datetime import datetime

from aiohttp import web
from decimal import Decimal

from app.billing.service_layers import Register, QuotesUpload, MakeDeposit, MoneyTransfer, Report
from core.aiohttp import dataclass_connector


@dataclass_connector(Register)
async def register(request, json_data, dataclass):
    await dataclass(
        name=json_data['name'],
        city=json_data['city'],
        country=json_data['country'],
        currency=json_data['currency'],
    ).execute(request['connection'])
    return web.json_response(status=201)


@dataclass_connector(MakeDeposit)
async def make_deposit(request, json_data, dataclass):
    await dataclass(
        user_id=json_data['user_id'],
        currency=json_data['currency'],
        value=Decimal(json_data['value']),
    ).execute(request['connection'], redis=request.app['redis'])
    return web.json_response(status=201)


@dataclass_connector(MoneyTransfer)
async def money_transfer(request, json_data, dataclass):
    await dataclass(
        sender_user_id=json_data['sender_user_id'],
        sender_currency=json_data['sender_currency'],
        sender_value=Decimal(json_data['sender_value']),
        recipient_user_id=json_data['recipient_user_id'],
    ).execute(request['connection'], redis=request.app['redis'])
    return web.json_response(status=201)


@dataclass_connector(QuotesUpload)
async def quotes_upload(request, json_data, dataclass):
    await dataclass(
        date=datetime.strptime(json_data['date'], '%Y-%m-%d'),
        currency=json_data['currency'],
        quote=Decimal(json_data['quote']),
    ).execute(request['connection'], redis=request.app['redis'])
    return web.json_response(status=201)


@dataclass_connector(Report)
async def report(request, json_data, dataclass):
    instances = await dataclass(
        user_name=json_data['user_name'],
        start_date=datetime.strptime(
            json_data['start_date'], '%Y-%m-%d') if json_data.get('start_date') else None,
        end_date=datetime.strptime(
            json_data['end_date'], '%Y-%m-%d') if json_data.get('end_date') else None,
    ).execute(request['connection'])
    return web.json_response(data=[x.to_json_dict() for x in instances], status=200)
