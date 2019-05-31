
BASE_CURRENCY = 'USD'
CURRENCIES = ('EUR', 'CNY', 'CAD')
ALL_CURRENCIES = CURRENCIES + (BASE_CURRENCY,)

TRANSACTION_TYPE_DEPOSIT = 'DEPO'
TRANSACTION_TYPE_TRANSFER = 'TRAN'


class AllCurrencyType(str):

    def __new__(cls, value: str):
        value = value.strip().upper()
        if value not in ALL_CURRENCIES:
            raise Exception(f'use one of: {ALL_CURRENCIES}')
        return super().__new__(cls, value)


class CurrencyType(str):

    def __new__(cls, value: str):
        value = value.strip().upper()
        if value not in CURRENCIES:
            raise Exception(f'use one of: {CURRENCIES}')
        return super().__new__(cls, value)
