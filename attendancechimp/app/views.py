from django.shortcuts import render
from django.http import HttpResponse
from datetime import date


def index(request):
    today = date.today()
    return render(request, 'app/index.html', {'dict':today})
