import inspect

from core.errors import ValidationError


def check_required_args(data_dict, cls):
    sig = inspect.signature(cls.__init__)
    req_params = set(p.name for p in sig.parameters.values() if p.name != "self" and p.default == inspect._empty)
    not_found_params = req_params.difference(set(data_dict.keys()))

    if not_found_params:
        raise ValidationError(f'please provide required parametres: {not_found_params}')
