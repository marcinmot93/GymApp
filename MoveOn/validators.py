from django.core.exceptions import ValidationError
from .models import *


def validate_login_exist(username):
    if not User.objects.filter(username=username).exists():
        raise ValidationError('Niepoprawna nazwa użytkownika')