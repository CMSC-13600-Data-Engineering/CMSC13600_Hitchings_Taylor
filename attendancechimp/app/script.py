#Scripts to create a random course, random students, and to have them join the class and attend some classes.

#To use this script: copy and paste the below code into views.py, but only after flushing the database.
#The script will autotmaically run after and manage.py command (including runserver), but can only be run once.
#So after using it, if you want to make use of the script again, remove the code from the views file, flush the database, add it back, and then run manage.py runserver again

#Scripts to do everything
def new_user(user, first_name,last_name,email,usernamey,passwordy,user_type='0'):
    new_user=User.objects.create(username=usernamey,password=passwordy)
    #new_user=User(user, first_name, last_name, email, user_type)
    new_user.save()
    newuser2=User_Profiles(user,first_name,last_name,email, user_type)
    newuser2.save()
    
def new_enrollment(enrollmentid,courseid,studentid):
    newe=Enrollment(enrollmentid,courseid,studentid)
    newe.save()

def new_instructor_qr(qrid,courseid,classmeeting,class_code):
    newinstqr=Instructor_QRCodes(qrid,courseid,classmeeting,class_code)
    newinstqr.save()

def newAttendance(attendanceid,enrollmentid,classmeeting,attended):
    newattendance=Attendance(attendanceid,enrollmentid,classmeeting,attended)
    newattendance.save()

import string
import random

def rstring(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
def rint(length):
    min=pow(10,length-1)
    max=pow(10,length)
    return random.randint(min,max)

new_user(1,rstring(4),rstring(4),rstring(4)+"@uchicag.edu",rstring(5),rstring(14),user_type=1)
cid=rint(9)
addCourse(str(cid),rstring(7),1,'MWF',"09:00",'2023-01-06','2023-06-01')
for i in range(10):
    new_instructor_qr(i+1,cid,i+1,rstring(10))
listy=[0,1]
for i in range(7):
    new_user(i+2,rstring(4),rstring(4),rstring(4)+"@uchicag.edu",rstring(5),rstring(14),user_type=0)
    new_enrollment(i+1,cid,i+1)
    for j in range(10):
        temp=random.choice(listy)
        if temp == 1:
            newAttendance(rint(5),i+1,j,attended=True)       

print(cid)
