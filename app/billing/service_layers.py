from dataclasses import dataclass
import datetime

from asyncpg import UniqueViolationError
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import insert

import settings
from app.billing.currency_convertor import CurrencyConverter
from app.billing.models import User, Quote, Transaction
from app.billing.types import TRANSACTION_TYPE_DEPOSIT, TRANSACTION_TYPE_TRANSFER, \
    generate_type_by_sa_column as sa_column, ALL_CURRENCIES, CURRENCIES
from core.dataclass import BaseCommand
from core.errors import ValidationError


@dataclass
class Register(BaseCommand):
    name: sa_column(User.name)
    country: sa_column(User.country)
    city: sa_column(User.city)
    currency: sa_column(User.currency, validators={'choices': {'choices': ALL_CURRENCIES}})

    async def execute(self, conn):
        try:
            await User.create(name=self.name, country=self.country, city=self.city, currency=self.currency)
        except UniqueViolationError:
            raise ValidationError("user name already exists")


@dataclass
class QuotesUpload(BaseCommand):
    date: datetime.datetime
    currency: sa_column(Quote.currency, validators={'choices': {'choices': CURRENCIES}})
    quote: sa_column(Quote.value)

    async def execute(self, conn, redis=None):
        await insert(Quote).values(currency=self.currency, date=self.date, value=self.quote).on_conflict_do_update(
            constraint=f'{Quote.__tablename__}_pkey', set_=dict(value=self.quote)
        ).gino.status()
        if self.date.date() == datetime.datetime.today().date():
            await redis.set(f'{settings.QUOTES_REDIS_PREFIX}_{self.currency}_{self.date.date()}', str(self.quote))


@dataclass
class MakeDeposit(BaseCommand):
    user_id: sa_column(Transaction.recipient_user_id)
    currency: sa_column(Transaction.sender_currency, validators={'choices': {'choices': ALL_CURRENCIES}})
    value: sa_column(Transaction.sender_value)

    async def execute(self, conn, redis=None):
        async with conn.transaction():
            user = await User.query.where(User.id == self.user_id).with_for_update().gino.first()
            if not user:
                raise ValidationError('user not found')
            currency_converter = CurrencyConverter(redis=redis)
            user_currency_amount = await currency_converter.convert(self.value, self.currency, user.currency)
            await Transaction.create(
                transaction_type=TRANSACTION_TYPE_DEPOSIT,
                sender_currency=self.currency,
                sender_value=self.value,
                recipient_user_id=self.user_id,
                recipient_currency=user.currency,
                recipient_value=user_currency_amount,
            )
            new_user_balance = await Transaction.calculate_user_balance_by_transactions(self.user_id)
            await User.update.values(balance=new_user_balance).where(User.id == self.user_id).gino.status()


@dataclass
class MoneyTransfer(BaseCommand):
    sender_user_id: sa_column(Transaction.sender_user_id)
    sender_currency: sa_column(Transaction.sender_currency, validators={'choices': {'choices': ALL_CURRENCIES}})
    sender_value: sa_column(Transaction.sender_value)
    recipient_user_id: sa_column(Transaction.recipient_user_id)

    async def execute(self, conn, redis=None):
        async with conn.transaction() as tx:
            if self.sender_user_id == self.recipient_user_id:
                raise ValidationError('sender can not be equal recipient')

            sender_user = await User.query.where(User.id == self.sender_user_id).with_for_update().gino.first()
            if not sender_user:
                raise ValidationError('sender user not found')

            recipient_user = await User.query.where(User.id == self.recipient_user_id).with_for_update().gino.first()
            if not recipient_user:
                raise ValidationError('recipient user not found')

            currency_converter = CurrencyConverter(redis=redis)
            send_value_in_user_currency = await currency_converter.convert(
                self.sender_value, self.sender_currency, sender_user.currency)

            if send_value_in_user_currency > sender_user.balance:
                raise ValidationError('you have not cash for transfer')

            recipient_user_currency_amount = await currency_converter.convert(
                self.sender_value, self.sender_currency, recipient_user.currency)

            await Transaction.create(
                transaction_type=TRANSACTION_TYPE_TRANSFER,
                sender_user_id=self.sender_user_id,
                sender_currency=sender_user.currency,
                sender_value=send_value_in_user_currency,
                recipient_user_id=self.recipient_user_id,
                recipient_currency=recipient_user.currency,
                recipient_value=recipient_user_currency_amount,
            )

            new_sender_balance = await Transaction.calculate_user_balance_by_transactions(self.sender_user_id)
            await User.update.values(balance=new_sender_balance).where(User.id == self.sender_user_id).gino.status()
            if new_sender_balance < 0:
                await tx.rollback()
                raise ValidationError('you have not cash for transfer')

            new_recipient_balance = await Transaction.calculate_user_balance_by_transactions(self.recipient_user_id)
            await User.update.values(
                balance=new_recipient_balance).where(User.id == self.recipient_user_id).gino.status()


@dataclass
class Report(BaseCommand):
    user_name: sa_column(User.name)
    start_date: datetime.date = None
    end_date: datetime.date = None

    async def execute(self, conn):
        user = await User.query.where(User.name == self.user_name).gino.first()
        if not user:
            raise ValidationError('user not found')

        query = Transaction.query.where(
            or_(Transaction.recipient_user_id == user.id, Transaction.sender_user_id == user.id))
        if self.start_date:
            query = query.where(Transaction.timestamp >= self.start_date.replace(hour=0, minute=0, second=0))
        if self.end_date:
            query = query.where(Transaction.timestamp <= self.end_date.replace(hour=23, minute=59, second=59))
        transactions = await query.order_by('timestamp').gino.all()
        return transactions
