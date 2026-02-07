from django.core.exceptions import ValidationError


def validate_gpa(value):
    if not 0.0 <= value <= 4.0:
        raise ValidationError('GPA must be between 0.0 and 4.0')


def validate_percentage(value):
    if not 0 <= value <= 100:
        raise ValidationError('Percentage must be between 0 and 100')


def validate_credit_hours(value):
    if value <= 0:
        raise ValidationError('Credit hours must be greater than 0')
