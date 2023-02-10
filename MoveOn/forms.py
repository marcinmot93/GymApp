from django import forms
from django.contrib.auth.models import User
from django.core.validators import *
from django.core.exceptions import ValidationError
from MoveOn.models import *
from .validators import *

TYPE = (
    (1, 'ThePupil'),
    (2, 'Trainer'),

)

TRAINERS = [
    (trainer.id, f'{trainer.name}') for trainer in Trainer.objects.all()
]

DAYS = [
    (day.id, f'{day.name}') for day in DayNumber.objects.all()
]

WEEKS = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
)

class CreateUserForm(forms.Form):
    login = forms.CharField(label='Login')
    password = forms.CharField(widget=forms.PasswordInput, label='Password', validators=[MinLengthValidator(8)])
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat Password', validators=[MinLengthValidator(8)])
    email = forms.EmailField(label='E-mail')
    account_type = forms.ChoiceField(choices=TYPE)
    first_name = forms.CharField(max_length=128, label='Name')
    last_name = forms.CharField(max_length=128, label='Last Name')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password != password2:
            raise ValidationError('Password are not the same. Please try again')

    def clean_login(self):
        user_name = self.cleaned_data.get('login')
        user = User.objects.filter(username=user_name)
        if user:
            raise ValidationError('Name already exist')
        return user_name


class AddExerciseForm(forms.Form):
    name = forms.CharField(label='Exercise name')
    description = forms.CharField(widget=forms.Textarea, required=False)
    movie_link = forms.CharField(label='Link')


class AddTrainingPlanForm(forms.Form):
    name = forms.CharField(label='Plan name')
    description = forms.CharField(widget=forms.Textarea, required=False)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    week_training_days = forms.ChoiceField(choices=WEEKS)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PupilDetailsForm(forms.Form):
    name = forms.CharField()
    last_name = forms.CharField()
    starting_weight = forms.IntegerField()
    height = forms.IntegerField()
    trainer = forms.ChoiceField()

class CreateExercisePlanForm(forms.Form):
    exercise = forms.ChoiceField()
    series = forms.IntegerField()
    reps = forms.IntegerField()
    training_day = forms.ChoiceField(choices=DAYS)


class testForm(forms.Form):
    series = forms.IntegerField()
    exercise = forms.ChoiceField()
