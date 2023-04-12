from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# Create your models here.

#Create a table of all users (students and instructors)

class User_Profiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", primary_key=True)
    first_name=models.CharField(max_length=50,null=True,blank=True)
    last_name=models.CharField(max_length=50,null=True,blank=True)
    email=models.CharField(max_length=50, null=True, blank=True, unique=True, error_messages={'unique':"This email has already been registered."})
    user_type = models.CharField(max_length=20,null=True,blank=True)
 
#create a table of all courses
class Courses(models.Model):
    courseid=models.CharField(max_length=9, primary_key=True)
    course_name=models.CharField(max_length=75,null=True,blank=True)
    instructorid=models.ForeignKey(User_Profiles,on_delete=models.CASCADE)
    recurrence=models.CharField(max_length=5,null=True,blank=True)
    classtime=models.CharField(max_length=5,null=True,blank=True)
    
#Track what students are enrolled in what classes
#This does allow a 'double enrollment' into a class
#So code actuall populating the table needs to prevent that
class Enrollment(models.Model):
    enrollmentid=models.AutoField(primary_key=True)
    enrolledclass=models.ForeignKey(Courses, on_delete=models.CASCADE)
    studentid=models.ForeignKey(User_Profiles,on_delete=models.CASCADE)

class Instructor_QRCodes(models.Model):
    qrid=models.AutoField(primary_key=True)
    courseid=models.ForeignKey(Courses,on_delete=models.CASCADE)
    classmeeting=models.IntegerField()
    qrcode=models.ImageField(upload_to='course_qr_codes')
    creation_time=models.DateTimeField()
    
class Attendance(models.Model):
    attendanceid=models.AutoField(primary_key=True)
    enrollmentid=models.ForeignKey(Enrollment,on_delete=models.CASCADE)
    classmeeting=models.ForeignKey(Instructor_QRCodes, on_delete=models.CASCADE)
    attended=models.BooleanField(default=False)
    
class Uploaded_QRCodes(models.Model):
    uploadid=models.AutoField(primary_key=True)
    enrollmentid=models.ForeignKey(Enrollment,on_delete=models.CASCADE)
    classmeeting=models.ForeignKey(Instructor_QRCodes,on_delete=models.CASCADE)
    upload_qr=models.ImageField(upload_to='uploaded_qr_codes')
    upload_time=models.DateTimeField()

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        User_Profiles.objects.create(user=instance)
    instance.profile.save()
#import logging
def addCourse(courseid,course_name,instructorid,recurrence,classtime):
    if len(courseid) != 9:
        raise ValueError('Course id is incorrect length, course id must be 9 characters')
    
    if len(course_name) >75:
        raise ValueError('Course name is incorrect length')

    if len(course_name) == 0:
        raise ValueError('Course name is incorrect length')

    if len(instructorid) == 0:
        raise ValueError('Course name is incorrect length')
    
    if Courses.objects.filter(courseid=courseid).count() > 0:
        raise ValueError('Another course with courseid ' + courseid + ' exists')
    
    if Courses.objects.filter(course_name=course_name).count() > 0:
        raise ValueError('Another course with the same name already exists')
    
    if len(recurrence) > 5:
        raise ValueError('Recurrence of the course is too long, please use 1 letter codes for each weekday the course meets on (M=monday, R=Thursday, etc.). Do not separate letters by spaces or commas')

    days=['M','T','W','R','F']
    for i in recurrence:
        if i not in days:
            raise ValueError('Unrecognized character in class recurrence, use the provided 1-letter codes for each day the class occurs and do not separate letters')
    if len(classtime) != 5:
        raise ValueError('Incorrect length for class start time, plase add time in the form 00:00 (24-hour time)')
    
    #This doesn't quite work because it doesn't account for 2 classes conflicting only on certian days of the week (or typos I guess)
    if Courses.objects.filter(classtime=classtime,instructorid=instructorid,recurrence=recurrence).count() > 0:
        raise ValueError('Another class is taught by the same instructor at the same time')
    new_course = Courses(courseid=courseid, course_name=course_name, instructorid=User_Profiles.objects.get(user=instructorid), recurrence=recurrence, classtime=classtime)
    new_course.save()
    
    
    
    #courseid=models.CharField(max_length=9, primary_key=True)
    #course_name=models.CharField(max_length=75,null=True,blank=True)
    #instructorid=models.ForeignKey(User,on_delete=models.CASCADE)
