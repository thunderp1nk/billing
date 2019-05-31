from dataclasses import dataclass

from decimal import Decimal

from datetime import datetime

from sqlalchemy import or_

from app.billing.currency_convertor import CurrencyConverter
from app.billing.models import User, Quote, Transaction
from app.billing.types import CurrencyType, AllCurrencyType, TRANSACTION_TYPE_DEPOSIT, TRANSACTION_TYPE_TRANSFER


@dataclass
class Register:
    name: str
    country: str
    city: str
    currency: AllCurrencyType

    async def execute(self, conn):
        await User.create(name=self.name, country=self.country, city=self.city, currency=self.currency)


@dataclass
class QuotesUpload:
    date: datetime
    currency: CurrencyType
    quote: Decimal

    async def execute(self, conn):
        # Инъекции пока не боимся, т к прошло все через датаклассы, но все равно стоит заэкскейпить все, мало ли
        # TODO: привести к алхимическому виду
        sql = f"""
            INSERT INTO {Quote.__tablename__} (currency, date, value)
            VALUES ('{self.currency}', to_date('{self.date.strftime('%Y-%m-%d')}', 'YYYY-MM-DD'), {str(self.quote)})
            ON CONFLICT ON CONSTRAINT {Quote.__tablename__}_pkey
            DO UPDATE SET value={str(self.quote)}
        """
        await conn.scalar(sql)


@dataclass
class MakeDeposit:
    user_id: int
    currency: AllCurrencyType
    value: Decimal

    async def execute(self, conn):
        async with conn.transaction():
            user = await User.query.where(User.id == self.user_id).with_for_update().gino.first()
            if not user:
                raise Exception('user not found')
            currency_converter = CurrencyConverter()
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
class MoneyTransfer:
    sender_user_id: int
    sender_currency: AllCurrencyType
    sender_value: Decimal
    recipient_user_id: int

    async def execute(self, conn):
        async with conn.transaction() as tx:
            if self.sender_user_id == self.recipient_user_id:
                raise Exception('sender can not be equal recipient')

            sender_user = await User.query.where(User.id == self.sender_user_id).with_for_update().gino.first()
            if not sender_user:
                raise Exception('sender user not found')

            recipient_user = await User.query.where(User.id == self.recipient_user_id).with_for_update().gino.first()
            if not recipient_user:
                raise Exception('recipient user not found')

            currency_converter = CurrencyConverter()
            send_value_in_user_currency = await currency_converter.convert(
                self.sender_value, self.sender_currency, sender_user.currency)

            if send_value_in_user_currency > sender_user.balance:
                raise Exception('you have not cash for transfer')

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
                raise Exception('error in transaction')

            new_recipient_balance = await Transaction.calculate_user_balance_by_transactions(self.recipient_user_id)
            await User.update.values(
                balance=new_recipient_balance).where(User.id == self.recipient_user_id).gino.status()


@dataclass
class Report:
    user_name: str
    start_date: datetime = None
    end_date: datetime = None

    async def execute(self, conn):
        user = await User.query.where(User.name == self.user_name).gino.first()
        if not user:
            raise Exception('user not found')

        query = Transaction.query.where(
            or_(Transaction.recipient_user_id == user.id, Transaction.sender_user_id == user.id))
        if self.start_date:
            query = query.where(Transaction.timestamp >= self.start_date.replace(hour=0, minute=0, second=0))
        if self.end_date:
            query = query.where(Transaction.timestamp <= self.end_date.replace(hour=23, minute=59, second=59))
        transactions = await query.gino.all()
        return transactions
