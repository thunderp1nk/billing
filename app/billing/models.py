from datetime import datetime

from gino.ext.aiohttp import Gino
from sqlalchemy import or_

import settings

db = Gino()


class User(db.Model):
    """
    1) Можно кошелек сделать отдельное таблицей, если нужно заложить возможность использования
     пользователем нескольких кошельков. Да и пользователь должен быть в отдельном приложении
    2) Можно сделать страну и город отдельными таблицами с предвнесенными значениями
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    country = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    balance = db.Column(db.Numeric(precision=12, scale=2), default=0, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Transaction(db.Model):
    """
    Описание
    """
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(4))

    sender_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    sender_currency = db.Column(db.String(3))
    sender_value = db.Column(db.Numeric(precision=12, scale=2))

    recipient_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    recipient_currency = db.Column(db.String(3), nullable=False)
    recipient_value = db.Column(db.Numeric(precision=12, scale=2), nullable=False)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    async def calculate_user_balance_by_transactions(cls, user_id):
        transactions = await Transaction.query.where(
            or_(Transaction.recipient_user_id == user_id, Transaction.sender_user_id == user_id)).gino.all()
        return sum([t.recipient_value if t.recipient_user_id == user_id else -t.sender_value for t in transactions])

    def to_json_dict(self):
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'sender_user_id': self.sender_user_id,
            'sender_currency': self.sender_currency,
            'sender_value': str(self.sender_value),
            'recipient_user_id': self.recipient_user_id,
            'recipient_currency': self.recipient_currency,
            'recipient_value': str(self.recipient_value),
            'timestamp': str(self.timestamp),
        }


class Quote(db.Model):
    """
    Описание
    """
    __tablename__ = 'quote'

    currency = db.Column(db.String(3), nullable=False)
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Numeric(precision=16, scale=6), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('currency', 'date'),
        {},
    )


def init_db(app):
    db_url = settings.DB_URL
    app['config']['gino'] = {'dsn': db_url}

    db.init_app(app)

    app.middlewares.append(db)


async def init_engine():
    engine = await db.set_bind(settings.DB_URL)
    return engine
