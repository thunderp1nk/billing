from core.validators import VALIDATORS

BASE_CURRENCY = 'USD'
CURRENCIES = ('EUR', 'CNY', 'CAD')
ALL_CURRENCIES = CURRENCIES + (BASE_CURRENCY,)

TRANSACTION_TYPE_DEPOSIT = 'DEPO'
TRANSACTION_TYPE_TRANSFER = 'TRAN'


def magical_new_for_sq_column_type(cls, value):
    for k, v in cls._validators.items():
        VALIDATORS[k](value, **v)

    return cls._origin_type(value)


def generate_type_by_sa_column(column, validators=None):
    if validators is None:
        validators = {}

    origin_type = column.type.python_type
    add_validators(column, validators)
    return type(
        f'sa_{str(column).replace(".", "_")}',
        (origin_type, ),
        {
            '_origin_type': origin_type,
            '_validators': validators,
            '__new__': magical_new_for_sq_column_type,
        }
    )


def add_validators(column, validators):
    if hasattr(column.type, "length"):
        validators['length'] = {'max_length': column.type.length}

    if hasattr(column.type, "scale"):
        validators['scale'] = {'scale': getattr(column.type, "scale", 0)}
