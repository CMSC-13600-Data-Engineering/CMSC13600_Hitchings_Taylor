from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('create/',views.addCourseForm, name='create'),
    path('create/handleaddCourse', views.handlecourseForm),
    path('create/create_success/<int:courseid>/', views.create_success, name='create_success'),
    # from 3 QR codes
    path('join/', views.joincourse, name='joincourse'),
   # path('attendance/', views.attendance, name='attendance'),
   path('upload/', views.upload_qr_code, name='upload_qr_code'),
]
