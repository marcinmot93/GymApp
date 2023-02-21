from django import forms
from django.core.validators import *
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
    login = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password',
                               validators=[MinLengthValidator(8)])
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repeat Password',
                                validators=[MinLengthValidator(8)])
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    account_type = forms.ChoiceField(choices=TYPE, widget=forms.Select(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=128, label='Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=128, label='Last Name',
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

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
    name = forms.CharField(label='Exercise name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    movie_link = forms.CharField(label='Link', widget=forms.TextInput(attrs={'class': 'form-control'}))


class AddTrainingPlanForm(forms.Form):
    name = forms.CharField(label='Plan name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    week_training_days = forms.ChoiceField(choices=WEEKS, widget=forms.Select(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    username = forms.CharField(validators=[validate_login_exist])
    password = forms.CharField(widget=forms.PasswordInput)


class PupilDetailsForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    starting_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    height = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    trainer = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))


class CreateExercisePlanForm(forms.Form):
    exercise = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))
    series = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    reps = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    training_day = forms.ChoiceField(choices=DAYS, widget=forms.Select(attrs={'class': 'form-control'}))


class ActualWeightForm(forms.Form):
    actual_weight = forms.FloatField(
        label='Update your weight:',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your weight here'})
    )


