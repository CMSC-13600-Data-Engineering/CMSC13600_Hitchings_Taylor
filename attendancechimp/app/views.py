from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'app/index.html', {})

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
