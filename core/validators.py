from core.errors import ValidationError


def length_validator(val, max_length=None):
    if len(val) > max_length:
        raise ValidationError('value too long')


def choices_validator(val, choices=None):
    if val not in choices:
        raise ValidationError(f'use one of: {choices}')


def scale_validator(val, scale=None):
    scale_part_len = len(str(val - int(val))[2:])
    if scale_part_len != scale:
        raise ValidationError(f'scale part must be {scale_part_len} digits')


VALIDATORS = {
    'length': length_validator,
    'choices': choices_validator,
    'scale': scale_validator
}
