from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('create',views.addCourseForm),
    path('handleaddCourse', views.handlecourseForm),
]
