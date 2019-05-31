from datetime import datetime

from decimal import Decimal, ROUND_DOWN

from app.billing.models import Quote
from app.billing.types import ALL_CURRENCIES, BASE_CURRENCY


class CurrencyConverter:

    async def get_quote(self, currency):
        if currency == BASE_CURRENCY:
            return Decimal(1)

        # TODO: можно и в один запрос, а еще лучше кешировать
        quote = await Quote.query.where(Quote.currency == currency).where(Quote.date == datetime.utcnow()).gino.first()
        return quote.value

    async def convert(self, amount, currency, new_currency):
        if currency == new_currency:
            return amount

        for c in currency, new_currency:
            if c not in ALL_CURRENCIES:
                raise ValueError('f{c} is not a supported currency')

        r0 = await self.get_quote(currency)
        r1 = await self.get_quote(new_currency)

        return (amount * r0 / r1).quantize(Decimal('.01'), rounding=ROUND_DOWN)
