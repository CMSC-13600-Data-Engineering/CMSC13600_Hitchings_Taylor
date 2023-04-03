from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages


def index(request):
    return render(request, 'app/index.html', {})


from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from app.forms import SignUpForm

def new(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            user.profile.user_type = form.cleaned_data.get('user_type')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return HttpResponse('User added.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
