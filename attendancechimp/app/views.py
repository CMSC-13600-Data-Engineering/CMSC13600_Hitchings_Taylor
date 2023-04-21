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
import random
import string
from django.utils import timezone
from django.db import IntegrityError


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


@login_required(login_url='/accounts/login/')
def addCourseForm(request, error_msg=''):
    '''addCourseForm serves a web form that we can use to add a course to the database
    '''
    # check if user profile is student
    if request.user.profile.user_type != '1':
        return HttpResponse("Error: You are not logged in as an instructor.")    
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
    instructorid=request.user.id
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
        
        enrollment = Enrollment(courseid=Courses.objects.get(courseid=course_get), studentid=studentid)
        enrollment.save()
        return HttpResponse('You have successfully enrolled!')

    return render(request, 'joincourse.html', {'courseid':courseid,'course_name':course_name})

    

from django.core.files.storage import FileSystemStorage


@login_required(login_url='/login/')
def upload_qr_code(request):
    # code to handle the student uploading the QR code image
    if request.user.profile.user_type != '0':
        return HttpResponse("Error: You are not logged in as a student.")
    
    if request.method == "GET":
        course_get = request.GET.get('courseid')
        courseid = Courses.objects.get(courseid=course_get).courseid
        course_name=Courses.objects.filter(courseid=courseid).values_list('course_name',flat = True)[0]
        studentid_get = request.user.id
        studentid = User_Profiles.objects.get(user_id=studentid_get)
        enrollmentid=Enrollment.objects.values_list('enrollmentid',flat=True).filter(studentid=studentid,courseid=courseid)[0]
        return render(request, 'upload_qr_code.html',{'courseid':courseid,'course_name':course_name,'enrollmentid':enrollmentid})
    if request.method == "POST": 
        course_get = request.POST.get('courseid')
        courseid = Courses.objects.get(courseid=course_get).courseid
        course_name=Courses.objects.filter(courseid=courseid).values_list('course_name',flat = True)[0]
        studentid_get = request.user.id
        studentid = User_Profiles.objects.get(user_id=studentid_get)
        if Enrollment.objects.filter(studentid=studentid, courseid=courseid).count() == 0:
            return HttpResponse("Error: You are not enrolled in this course.")

        #upload_qr=request.FILES["upload_qr"]
        
        upload_qr = request.FILES['upload_qr']
        fss = FileSystemStorage()
        #file = fss.save(upload_qr.name, upload_qr)
        #file_url = fss.url(file)
        #upload_qr=request.POST['upload_qr']
        enrollmentid=Enrollment.objects.values_list('enrollmentid',flat=True).filter(studentid=studentid,courseid=courseid)[0]
        
        enrollment_get=request.POST.get('enrollmentid')
        newqrcode=Uploaded_QRCodes(enrollmentid=Enrollment.objects.get(enrollmentid=enrollment_get),upload_qr=upload_qr)
        newqrcode.save()
    
    
        #return HttpResponse("Success! Image Uploaded")
        return redirect(reverse('upload_success'))
    #else:
        
        
    
def upload_success(request):
    # code to display the success page for uploaded qr code    
    return render(request, 'upload_success.html')


#Code to handle the instructor creating the QR code image
@login_required(login_url='/login/')
def attendance_qr(request):
    # check if user is instructor
    if request.user.profile.user_type != '1':
        return HttpResponse("Error: You are not logged in as an instructor.")

    if request.method == "GET":
        course_get = request.GET.get('courseid')
        courseid = Courses.objects.get(courseid=course_get)
        coursename = Courses.objects.get(courseid=course_get).course_name
        instructor_id = Courses.objects.get(courseid=course_get).instructorid_id
        user_id = request.user.profile.user_id

        # check if logged-in instructor is the instructor of the class
        if instructor_id != user_id:
            return HttpResponse("Error: You are not the instructor of this class.")
        else:
            class_name = coursename
            # Generate class_code and class_code_time only if not already stored in session
            if 'class_code' not in request.session or 'class_code_time' not in request.session:
                class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                class_code_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S") # Convert datetime object to string
                request.session['class_code'] = class_code
                request.session['class_code_time'] = class_code_time
            else:
                class_code = request.session['class_code']
                class_code_time = request.session['class_code_time']

            context = {'courseid':courseid, 'class_code': class_code, 'class_code_time': class_code_time, 'class_name': class_name}
            print('GET SUCCEED!')
            return render(request, 'attendance_qr.html', context)

    if request.method == "POST":
        course_get = request.GET.get('courseid')
        courseid = Courses.objects.get(courseid=course_get)
        coursename = Courses.objects.get(courseid=course_get).course_name

        class_name = coursename
        # Retrieve class_code and class_code_time from session
        class_code = request.session.get('class_code', None)
        class_code_time = request.session.get('class_code_time', None)
        if not class_code or not class_code_time:
            return HttpResponse("Error: QR could not render.")
        
        # Create a new object in the Instructor_QRCodes model
        instructor_qrcode = Instructor_QRCodes(courseid=courseid,
                                                class_code=class_code,
                                                class_code_time=class_code_time)
        try:  
            # Save the object to the database
            instructor_qrcode.save()
            success_message = 'Class QR code initiated successfully!'
        except IntegrityError:
            # Handle IntegrityError if the class_code already exists in the database
            success_message = "You have already initiated the QR for this class session."
    
        
        # Render the template with the generated class code
        context = {'courseid':courseid, 'class_code': class_code, 'class_code_time': class_code_time, 'class_name': class_name, 'success_message': success_message}
        return render(request, 'attendance_qr.html', context)
    
    return HttpResponse("Error: QR could not render.")

    


