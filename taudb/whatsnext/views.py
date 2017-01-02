from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
import MySQLdb as mdb

from query import get_neighbourhoods


def get_points_by_center_and_distance(latitude,longitude,dist):
    return latitude-dist/111.0, latitude+dist/111.0, longitude-dist/69.0, longitude+dist/69.0


def json(request):
    return HttpResponse("{'Alon':'Itzhaki'}")


def homepage(request):
    contexts = {
        'neighbourhoods': get_neighbourhoods()
    }
    return render(request, 'whatsnext/index.html', context=contexts)


def get_hotels(request):
    hotels = dict()

    conn = mdb.connect(host='127.0.0.1', user='DbMysql06', passwd='DbMysql06', db='DbMysql06', port=3305)
    cur = conn.cursor(mdb.cursors.DictCursor)

    '''
    Get Hotels around the coordinates below.
    latitude = 51.533033
    longitude = -0.136822
    boundaries = get_points_by_center_and_distance(latitude, longitude, 5.0)

    cur.execute('SELECT * FROM places WHERE latitude BETWEEN %f AND %f AND longitude BETWEEN %f AND %f LIMIT 100',
                boundaries)
    '''
    cur.execute('SELECT * FROM places LIMIT 100')

    rows = cur.fetchall()
    for place in rows:
        hotel = dict()
        hotel["name"] = place["name"]
        hotel["latitude"] = place["latitude"]
        hotel["longitude"] = place["longitude"]
        hotels[place["id"]] = hotel

    return JsonResponse(hotels, status=201)

