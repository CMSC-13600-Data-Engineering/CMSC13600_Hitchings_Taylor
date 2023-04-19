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
        return addCourseForm(request,error_msg="Error: There is a database error in creating this course: " + str(e) + '\n')

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
    courseid = Courses.objects.get(courseid=course_get).courseid
    course_name=Courses.objects.filter(courseid=courseid).values_list('course_name',flat = True)[0]
    
    if request.method == 'POST':
        studentid_get = request.user.id
        studentid = User_Profiles.objects.get(user_id=studentid_get)

        current_enrollment = Enrollment.objects.filter(studentid=studentid, courseid=courseid).count()

        # Check if student is already enrolled in this course
        if current_enrollment > 0:
            return render(request, 'joincourse.html', {'error': 'You are already enrolled in this course.'})
        # Check if student is enrolled in any other courses with the same classtime
        current_courses = Enrollment.objects.filter(studentid=studentid)
        
        #courseidy=courseid.courseid
        for enrollment in Enrollment.objects.filter(studentid=studentid, courseid=courseid):
            if enrollment.courseid.classtime == Courses.objects.get(courseid=courseid).classtime:
                #messages.error(request, 'You are already enrolled in a course that meets at this time.')
                return render(request, 'joincourse.html', {'courseid':courseid,'course_name':course_name,'error':'You are already enrolled in a course that meets at this time'})

        # Enroll student in course
        instructorid=User_Profiles.objects.get(user=instructorid)
        enrollment = Enrollment(courseid=Courses.objects.get(courseid=course_get), studentid=studentid)
        enrollment.save()
        return HttpResponse('You have successfully enrolled!')

    else:
        #courseid = request.GET.get('courseid')
        #course_name=request.GET.get('course_name').course_name
        return render(request, 'joincourse.html', {'courseid':courseid,'course_name':course_name})

    


'''
@login_required(login_url='/accounts/login/')
def attendance(request):
    # code to display the QR code for attendance
    # ...
    course_id = request.GET.get('course_id')
    return render(request, 'attendance.html', {'course_id': course_id})
'''






@login_required(login_url='/login/')
def upload_qr_code(request):
    # code to handle the student uploading the QR code image
    if request.user.profile.user_type != '0':
        return HttpResponse("Error: You are not logged in as a student.")
    course_get = request.GET.get('courseid')
    courseid = Courses.objects.get(courseid=course_get).courseid
    course_name=Courses.objects.filter(courseid=courseid).values_list('course_name',flat = True)[0]
    studentid_get = request.user.id
    studentid = User_Profiles.objects.get(user_id=studentid_get)
    enrollmentid=Enrollment.objects.values_list('enrollmentid',flat=True).filter(studentid=studentid,courseid=courseid)[0]
    
    if request.method == "POST": 

        if Enrollment.objects.filter(studentid=studentid, courseid=courseid).count() == 0:
            return HttpResponse("Error: You are not enrolled in this course.")

        upload_qr=request.FILES
    
        newqrcode=Uploaded_QRCodes(enrollmentid=enrollmentid,upload_qr=upload_qr)
        newqrcode.save()
    
    
        #return HttpResponse("Success! Image Uploaded")
        return redirect(reverse('upload_success'))
    else:
        
        return render(request, 'upload_qr_code.html',{'courseid':courseid,'course_name':course_name,'enrollmentid':enrollmentid})
    
def upload_success(request):
    # code to display the success page for uploaded qr code
    
    return render(request, 'upload_success.html')
