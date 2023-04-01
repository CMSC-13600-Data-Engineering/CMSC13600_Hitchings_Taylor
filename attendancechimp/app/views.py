from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import calendar


def index(request):
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    month = now.strftime("%B")
    day = now.strftime("%d")
    login_date = 'Today is ' + month + " " + day + '.' 
    login_time = 'User joined at ' + time + '.'
    return render(request, 'app/index.html', {'date':login_date,'time':login_time})
