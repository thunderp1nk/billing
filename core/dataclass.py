from dataclasses import dataclass, fields

from core.errors import ValidationError


@dataclass
class BaseCommand:

    def __post_init__(self):
        for field in fields(self):
            attr = getattr(self, field.name)
            if not attr or isinstance(attr, field.type):
                continue
            elif hasattr(field.type, '_origin_type') and isinstance(attr, field.type._origin_type):
                setattr(self, field.name, field.type(attr))
            else:
                raise ValidationError(f'wrong type of field {field}')
