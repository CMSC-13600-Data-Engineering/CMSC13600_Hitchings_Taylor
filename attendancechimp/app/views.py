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

    # check if user profile is student
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

        for enrolled_course in current_courses:
            enrolled_course_courseid = enrolled_course.courseid.courseid
            if Courses.objects.get(courseid=enrolled_course_courseid).classtime == Courses.objects.get(courseid=courseid).classtime:
                if Courses.objects.get(courseid=enrolled_course_courseid).recurrence == Courses.objects.get(courseid=courseid).recurrence:
                    return render(request, 'joincourse.html', {'courseid':courseid,'course_name':course_name,'error':'You are already enrolled in a course that meets at this time.'})
       

        # Enroll student in course
        enrollment = Enrollment(courseid=Courses.objects.get(courseid=course_get), studentid=studentid)
        enrollment.save()
        return HttpResponse('You have successfully enrolled!')

    return render(request, 'joincourse.html', {'courseid':courseid,'course_name':course_name})

    

from django.core.files.storage import FileSystemStorage

@login_required(login_url='/accounts/login/')
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


        
        # create new attendance object - for now set attended=1 if any image uploaded

        # Retrieve the most recent Instructor_QRCodes object for a given courseid   
        if Instructor_QRCodes.objects.filter(courseid_id=courseid).count() >= 1:
            latest_instructor_qrcode = Instructor_QRCodes.objects.filter(courseid_id=courseid).latest('class_code_time')
            latest_classmeeting = latest_instructor_qrcode.classmeeting
            
            new_attendance = Attendance(enrollmentid=Enrollment.objects.get(enrollmentid=enrollment_get), classmeeting=latest_classmeeting, attended=True)
            new_attendance.save()
        else:
            return HttpResponse('Your instructor has not initiated any QR codes.')
                                    
    
        #return HttpResponse("Success! Image Uploaded")
        return redirect(reverse('upload_success'))
        
        
    
def upload_success(request):
    # code to display the success page for uploaded qr code    
    return render(request, 'upload_success.html')


#Code to handle the instructor creating the QR code image
@login_required(login_url='/accounts/login/')
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
        
        # Get the last classmeeting value for the given courseid
        last_classmeeting = Instructor_QRCodes.objects.filter(courseid=courseid).order_by('-classmeeting').first()
        if last_classmeeting:
            classmeeting = last_classmeeting.classmeeting + 1
        else:
            classmeeting = 1
        
        # Create a new object in the Instructor_QRCodes model
        instructor_qrcode = Instructor_QRCodes(courseid=courseid,
                                               classmeeting=classmeeting,
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
        del request.session['class_code']
        del request.session['class_code_time']
        return render(request, 'attendance_qr.html', context)
    
    return HttpResponse("Error: QR could not render.")


from .models import Courses, Enrollment, Attendance, Instructor_QRCodes
from django.db.models import Count

@login_required(login_url='/accounts/login/')
def overview(request):
    # check if user is instructor
    if request.user.profile.user_type != '1':
        return HttpResponse("Error: You are not logged in as an instructor.")

    course_get = request.GET.get('courseid')
    courseid = Courses.objects.get(courseid=course_get).courseid
    course_name=Courses.objects.filter(courseid=courseid).values_list('course_name',flat = True)[0]
    # number of students in course
    enrollments = Enrollment.objects.filter(courseid=courseid)
    student_count = enrollments.count()
    
    enrollment_ids = enrollments.values_list('enrollmentid', flat=True)
    
    # Use queryset filtering with "in" lookup to get all Attendance objects with enrollmentid in the given enrollment_ids list
    attendances = Attendance.objects.filter(enrollmentid__in=enrollment_ids)

    # get all enrollment ids for course
    print('Enrollment IDS:',enrollment_ids)
    

    classmeetings = []
    class_instances = Instructor_QRCodes.objects.filter(courseid=courseid).values_list('classmeeting', flat=True)
    for class_instance in class_instances:
        attendance_count = attendances.filter(classmeeting=class_instance).count()
        classmeetings_item = {'classmeeting': class_instance, 'attendance_count': attendance_count}
        classmeetings.append(classmeetings_item)

    
    context = {'courseid':courseid, 'course_name':course_name, 'student_count':student_count, 'classmeetings':classmeetings}

    return render(request, 'overview.html', context)

@login_required(login_url='/accounts/login/')
def student(request):
    # check if user is instructor
    if request.method != "GET":
        return HttpResponse("Error: the request is not an HTTP GET request\n", status=500)
    
    if request.user.profile.user_type != '1':
        return HttpResponse("Error: You are not logged in as an instructor.")

    course_get = request.GET.get('courseid')
    courseid = Courses.objects.get(courseid=course_get).courseid
    course_name=Courses.objects.filter(courseid=courseid).values_list('course_name',flat = True)[0]
    
    #get all the students in the class
    enrollments=Enrollment.objects.filter(courseid=courseid)
    studentids=enrollments.values_list('studentid',flat=True)
    
    to_display=[]
    for i in studentids:
        first_name=User_Profiles.objects.filter(user=i).values_list('first_name',flat=True)[0]
        last_name=User_Profiles.objects.filter(user=i).values_list('last_name',flat=True)[0]
        class_instances = Instructor_QRCodes.objects.filter(courseid=courseid).values_list('classmeeting', flat=True)
        enrollment_id=Enrollment.objects.filter(courseid=courseid,studentid=i).values_list('enrollmentid',flat=True)[0]
        to_display_item={}
        to_display_item['studentid']=i
        to_display_item['first_name']=first_name
        to_display_item['last_name']=last_name
        classes_attended=[]
        for j in range(len(class_instances)):
            #stry=str('classmeeting')+str(j+1)
            meeting=class_instances[j]
            if Attendance.objects.filter(enrollmentid=enrollment_id,classmeeting=meeting).count()> 0:
                #to_display_item[stry]=1
                classes_attended.append(str(i+1))
        to_display_item['classes_attended']=classes_attended
        to_display.append(to_display_item)
    context = {'courseid':courseid, 'course_name':course_name, 'to_display':to_display}
    return render(request, 'student.html', context)

        
        





