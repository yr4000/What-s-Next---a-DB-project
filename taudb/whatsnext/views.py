from django.shortcuts import render
from django.http import HttpResponse
from django.templatetags.static import static

from query import get_neighbourhoods


def json(request):
    return HttpResponse("{'Alon':'Itzhaki'}")


def homepage(request):
    contexts = {
        'neighbourhoods': get_neighbourhoods()
    }
    return render(request, 'whatsnext/index.html', context=contexts)
