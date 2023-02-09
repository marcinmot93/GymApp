from django.core.exceptions import ValidationError
from .models import *

def validate_login_exist(param):
    if not User.objects.filter(param).exists():
        raise ValidationError('Incorrect username')