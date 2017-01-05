# Generic packages import
import json

# Django packages import
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404

# Internal packages import
from utils.db_utils import *
from utils.geo_utils import *
from utils.google_maps_access import fetch_reviews_from_google
from utils.api_responses import MISSING_QUERY_PARAMS, INVALID_QUERY_PARAMS
from utils.exceptions import NotFoundInDb
from utils.data_access import get_place_by_place_id, get_place_reviews

# Globals
RESOLUTION = 10000
BARS_VIEW = "places"  # TODO replace when time comes


def get_points_by_center_and_distance(latitude, longitude, dist):
    return latitude-dist/111.0, latitude+dist/111.0, longitude-dist/69.0, longitude+dist/69.0


def homepage(request):
    contexts = {
        'categories': ['Hotel', 'Restaraunt']
    }
    return render(request, 'whatsnext/index.html', context=contexts)


def get_hotels(request):
    hotels = dict()

    cur = init_db_cursor()

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


def search_by_word(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    places = dict()

    word_to_search = request_json["word"]
    category_for_search = request_json["category"]

    cur = init_db_cursor()

    # Get places whom contain the word in the request
    query = 'SELECT * FROM places, places_categories WHERE places_categories.place_id = places.id ' \
            'AND places_categories.category_id = {category} AND places.name like "%{name}%"' \
            ' LIMIT 20'.format(category=category_for_search, name=word_to_search)

    cur.execute(query)

    # cur.execute('Select * From places Where MATCH(places.name)
    # AGAINST("+%s" IN BOOLEAN MODE) LIMIT 10' % word_to_search)

    rows = cur.fetchall()
    for row in rows:
        place = dict()
        place["id"] = row["id"]
        place["google_id"] = row["google_id"]
        place["rating"] = row["rating"]
        place["vicinity"] = row["vicinity"]
        place["name"] = row["name"]
        place["latitude"] = row["latitude"]
        place["longitude"] = row["longitude"]
        places[row["id"]] = place

    return JsonResponse(places, status=201)


# returns places (e.g hotels, bars, attractions etc...).
# pre: latitude, longitude are NOT modified (i.e in the desirable resolution), and dist is in Km.
# post: a json string with the desired request
def search_places_by_point(latitude,longitude,dist,table = "",columns = ""):
    hotels = {}
    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, dist)
    # write the query
    query = "SELECT " + columns + " FROM " + table \
            + " WHERE latitude <= " + str(top) \
            + " AND longitude <= " + str(right) \
            + " AND latitude >= " + str(bottom) \
            + " AND longitude >= " + str(left)
    # send the query to database
    rows = execute_query(query)
    for row in rows:
        # TODO: there might be a problem with the names of the hotels: 'unicodeDecodeError: 'utf8' codec can't decode..'
        '''
        #here i tried to solve the decoding problem
        for element in row:
            x = row[element]
            row[element].decode('latin-1')
          '''
        hotel = dict()
        hotel["id"] = row["id"]
        hotel["google_id"] = row["google_id"]
        hotels[row["id"]] = hotel
    # return result:
    n = len(hotels)  # for debug TODO remember to delete
    return JsonResponse(hotels, status=201)


# returns a shortest pub crawl track from a starting point, according to number of bars
# pre: latitude and longitude are NOT modified
# TODO: consider save bar's name since there might be a couple of places in the same spot
def pub_crawl(latitude,longitude,numOfBars = 4):
    trackPoints = [[0, 0] for i in range(numOfBars)]
    trackPoints[0][0], trackPoints[0][1] = latitude, longitude  # initialize the first point in the track
    for i in range(1,numOfBars):
        currMinDist = -1
        closestPoint = [0, 0]
        # return all bars in range of 0.5 km TODO what if there aren't?
        top, right, buttom, left = get_boundaries_by_center_and_distance(latitude,longitude,0.5)
        excludeLats = [trackPoints[x][0] for x in range(i)]  # we don't want the same point to appear in the track twice
        excludeLongs = [trackPoints[x][1] for x in range(i)]
        query = "SELECT latitude, longitude FROM " + BARS_VIEW \
                + " WHERE latitude <= " + str(top) \
                + " AND longitude <= " + str(right) \
                + " AND latitude >= " + str(buttom) \
                + " AND longitude >= " + str(left)
                #+ " AND latitude NOT IN (" + excludeLats[1:len(excludeLats)-1]+")" \
                #+ " AND longitude NOT IN (" + excludeLongs[1:len(excludeLongs)-1]+")"
        for x in range(i):
            query = query + " AND latitude != " + str(excludeLats[x]) \
                            + " AND longitude != " + str(excludeLongs[x])
        #TODO: maybe it is better to use the query only once? the problem is that it's might not be correct (we always stay in the same square)
        rows = execute_query(query)
        # for each point in range look for the closest one.
        # we save the min distance at currMinDist and it's point at closestPoint
        for j in range(len(rows)):
            currPoint = (latitude,longitude)
            tempP = (rows[j]["latitude"],rows[j]["longitude"])
            tempDist = gps_distance(currPoint,tempP)
            if currMinDist == -1 or currMinDist > tempDist:
                currMinDist = tempDist
                closestPoint[0], closestPoint[1] = rows[j]["latitude"], rows[j]["longitude"]
        # add the current point to an array
        trackPoints[i][0], trackPoints[i][1] = closestPoint[0], closestPoint[1]
        latitude, longitude = closestPoint[0] , closestPoint[1]  # update the current point to be the closest we found
        # calculate again with the point found
    #TODO: print the points to map and a route if possible
    return HttpResponse(str(trackPoints))
    # return trackPoints


def get_place_details(request):
    if 'place_id' not in request.GET:
        return JsonResponse(MISSING_QUERY_PARAMS, status=400)

    # get required query parameter place_id
    place_id = request.GET['place_id']
    if not place_id:
        return JsonResponse(INVALID_QUERY_PARAMS, status=400)

    # fetch place from db
    try:
        place = get_place_by_place_id(place_id=place_id)
    except NotFoundInDb:
        return JsonResponse({'error': 'place with specified id does not exist'}, status=404)

    # fetch reviews for place from db
    reviews = get_place_reviews(place=place)
    if not reviews:
        # fetch reviews for place from Google Places API, and store in db
        reviews = fetch_reviews_from_google(place=place)

    # convert reviews to dictionaries so they can be serialized
    reviews_dicts = list()
    for review in reviews:
        reviews_dicts.append(review.to_json())

    return JsonResponse({'place': place.to_json(), 'reviews': reviews_dicts}, status=200)
