from django.shortcuts import render
from django.http import HttpResponse


def json(request):
    return HttpResponse("{'Alon':'Itzhaki'}")


def homepage(request):
    return render(request, 'whatsnext/index.html')
