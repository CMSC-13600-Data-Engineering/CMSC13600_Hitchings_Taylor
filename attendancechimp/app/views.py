from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages


def index(request):
    return render(request, 'app/index.html', {})


from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from app.forms import SignUpForm

import json

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
            return HttpResponse('Success! New user created.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def addCourseForm(request, error_msg=''):
    '''addCourseForm serves a web form that we can use to add a course to the database
    '''

    return render(request, 'addcourse.html', {'error': error_msg})

def handlecourseForm(request):
    if request.method != "POST":
        return HttpResponse("Error: the request is not an HTTP POST request\n", status=500)
    try:
        courseid = request.POST['courseid']
        course_name = request.POST['course_name']
        instructorid = request.POST['instructorid']
    except:

        return addBookForm(request, error_msg='Please fill out all the fields of the form')


    try:
        addCourse(courseid, course_name, instructorid)
    except Exception as e:
        return HttpResponse("Error: There is a database error in creating this course: " + str(e) + '\n', status=500)

    return HttpResponse(status=200)
