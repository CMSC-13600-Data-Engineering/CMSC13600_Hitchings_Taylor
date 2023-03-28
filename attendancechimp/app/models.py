from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
# Create your models here.

#Create a table of all users (students and instructors)
    #Defining the choices 'student' and 'instructor'
type_choices= (
    ('Student','Student'),
    ('Instructor','Instructor')
)
class User(models.Model):
    userid=models.IntegerField(validators=[MaxLengthValidator(8),MinLengthValidator(8)],
                           primary_key=True)
    first_name=models.CharField(max_length=20,null=True,blank=True)
    last_name=models.CharField(max_length=20, null=True, blank=True)
    user_class=models.CharField(
        max_length=20, choices=type_choices,default='Student')
 
#create a table of all courses
class Courses(models.Model):
    courseid=models.CharField(validators=[MaxLengthValidator(9),MinLengthValidator(9)],
                              primary_key=True)
    coursename=models.CharField(maxlength=75,null=True,blank=True)
    instructor=models.ForeignKey(User,on_delete=models.CASCADE,
                                 limit_choices_to={'user_class': 'Instructor'})
    #Should the first 'User' be 'User.userid'?

#Track what students are enrolled in what classes
#This does allow a 'double enrollment' into a class
#So code actuall populating the table needs to prevent that"""
class Enrollment(models.Model):
    enrollmentid=models.AutoField(primary_key=True)
    student=models.ForeignKey(User,on_delete=models.CASCADE,
                              limit_choices_to={'user_class':'Student'})
    enrolledclass=models.ForeignKey(Courses, on_delete=models.CASCADE)
    
class Instructor_QRCodes(models.Model):
    qrid=models.AutoField(primary_key=True)
    course=models.ForeignKey(Courses,on_delete=models.CASCADE)
    #qrcode=models.
    #time=models.DateTimeField(args)
    
    
    
class Uploaded_QRCodes(models.Model):
    uploadid=models.AutoField(primary_key=True)
    qrcodeid=models.ForeignKey(Instructor_QRCodes,on_delete=models.CASCADE)
    #qrcode=models.
    #time=models.DateTimeField(args)
    
    