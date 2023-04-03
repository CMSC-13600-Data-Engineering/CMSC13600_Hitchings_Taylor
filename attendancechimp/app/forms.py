from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


USER_TYPES = [
    (0, 'Student'),
    (1, 'Instructor'),
    ]

def validate_email(value):
    if User.objects.filter(email = value).exists():
        raise ValidationError((f"{value} is taken."),params = {'value':value})

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label='First Name')
    last_name = forms.CharField(max_length=50, label='Last Name')
    email = forms.EmailField(max_length=50, label='University Email', validators=[validate_email])
    user_type = forms.CharField(max_length=20, label='Are you a student or an instructor?',
    widget=forms.RadioSelect(choices=USER_TYPES))
    
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email', 'user_type', 'password1', 'password2', )


