from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import calendar


def index(request):
    now = datetime.now()
    month = now.strftime("%B")
    day = now.strftime("%d")
    time_str = 'Today is the ' + day + 'th of ' + month
    return render(request, 'app/index.html', {'dict':time_str,'red':'red'})
