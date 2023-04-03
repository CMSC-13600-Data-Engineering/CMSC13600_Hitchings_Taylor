from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

USER_TYPES = [
    (0, 'Student'),
    (1, 'Instructor'),
    ]

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label='First Name')
    last_name = forms.CharField(max_length=50, label='Last Name')
    email = forms.CharField(max_length=50, label='University Email')
    user_type = forms.CharField(max_length=20, label='Are you a student or an instructor?',
    widget=forms.RadioSelect(choices=USER_TYPES))
    
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email', 'user_type', 'password1', 'password2', )
