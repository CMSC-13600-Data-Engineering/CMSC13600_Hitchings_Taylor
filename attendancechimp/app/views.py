from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
import json
from app.models import *
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from app.forms import SignUpForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required



def index(request):
    return render(request, 'app/index.html', {})

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
    if request.user.profile.user_type != '1':
        return HttpResponse("Error: You are not logged in as an instructor.")
    try:
        courseid = request.POST['courseid']
        course_name = request.POST['course_name']
        instructorid = request.POST['instructorid']
        recurrence = request.POST['recurrence']
        classtime = request.POST['classtime']
        startdate=request.POST['startdate']
        enddate=request.POST['enddate']
    except:
        return addCourseForm(request, error_msg='Please fill out all the fields of the form')

    try:
        addCourse(courseid, course_name, instructorid, recurrence, classtime, startdate, enddate)
    except Exception as e:
        return HttpResponse("Error: There is a database error in creating this course: " + str(e) + '\n', status=500)

    return redirect(reverse('create_success', args=[courseid]))


def create_success(request, courseid):
    # code to display the success page with personalized URLs
    join_url = f'/app/join/?courseid={courseid}'
    attendance_url = f'/app/attendance?courseid={courseid}'
    upload_url = f'/app/upload?courseid={courseid}'
    return render(request, 'create_success.html', {'join_url': join_url, 'attendance_url': attendance_url, 'upload_url': upload_url})
    

@login_required(login_url='/accounts/login/')
def joincourse(request):
    # code to handle the student joining the course

    # check if user prifile is student
    if request.user.profile.user_type != '0':
        return HttpResponse("Error: You are not logged in as a student.")

    course_get = request.GET.get('courseid')
    courseid = Courses.objects.get(courseid=course_get)
 

    if request.method == 'POST':
        studentid_get = request.user.id
        studentid = User_Profiles.objects.get(user_id=studentid_get)

        current_enrollment = Enrollment.objects.filter(studentid=studentid, courseid=courseid).first()

        # Check if student is already enrolled in this course
        if current_enrollment is not None:
            return render(request, 'app/join.html', {'error_message': 'You are already enrolled in this course.'})
        
        # Check if student is enrolled in any other courses with the same classtime
        current_courses = Enrollment.objects.filter(studentid=studentid)
        for enrollment in current_courses:
            if enrollment.courseid.classtime == Courses.objects.get(courseid=courseid).classtime:
                messages.error(request, 'You are already enrolled in a course that meets at this time.')
                return render(request, 'app/join.html', {'courseid':courseid})

        # Enroll student in course
        enrollment = Enrollment(courseid=courseid, studentid=studentid)
        enrollment.save()
        return HttpResponse('You have successfully enrolled!')

    else:
        courseid = request.GET.get('courseid')
        return render(request, 'joincourse.html', {'courseid':courseid})

    


'''
@login_required(login_url='/accounts/login/')
def attendance(request):
    # code to display the QR code for attendance
    # ...
    course_id = request.GET.get('course_id')
    return render(request, 'attendance.html', {'course_id': course_id})

@login_required(login_url='/login/')
def upload_qr_code(request):
    # code to handle the student uploading the QR code image
    # ...
    course_id = request.GET.get('course_id')
    return render(request, 'upload_qr_code.html', {'course_id': course_id})
'''
