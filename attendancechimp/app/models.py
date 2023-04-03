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
    instructorid=models.ForeignKey(User,on_delete=models.CASCADE)
#Must ensure in some way that students cannot accidentally be instructors
    
#Track what students are enrolled in what classes
#This does allow a 'double enrollment' into a class
#So code actuall populating the table needs to prevent that
class Enrollment(models.Model):
    enrollmentid=models.AutoField(primary_key=True)
    enrolledclass=models.ForeignKey(Courses, on_delete=models.CASCADE)
    studentid=models.ForeignKey(User,on_delete=models.CASCADE)

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

