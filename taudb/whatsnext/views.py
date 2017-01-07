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
from utils.data_access import get_place_by_place_id, get_place_reviews, get_categories_statistics

# Globals
RESOLUTION = 10000
BARS_VIEW = "places"  # TODO replace when time comes
BASE_TABLE = "places"


def homepage(request):
    categories = []
    categories_results = execute_query("SELECT * FROM categories")
    for category in categories_results:
        categories.append(category["name"].capitalize())

    contexts = {
        'categories': categories
    }
    return render(request, 'whatsnext/index.html', context=contexts)


def search_by_word(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    places = dict()

    word_to_search = request_json["word"]
    category_for_search = request_json["category"].lower()

    cur = init_db_cursor()

    # Get places whom contain the word in the request
    query = 'SELECT * FROM places JOIN places_categories ON places.id = places_categories.place_id ' \
            'JOIN categories ON places_categories.category_id = categories.id WHERE  categories.name = "{category}" AND' \
            ' places.name like "%{name}%" LIMIT 20'.format(category=category_for_search, name=word_to_search)

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


# TODO Yair, delete this view once you understand why the other one is more of a view rather then a function.
# returns places (e.g hotels, bars, attractions etc...).
# pre: latitude, longitude are NOT modified (i.e in the desirable resolution), and dist is in Km.
# post: a json string with the desired request
def search_places_by_points(latitude,longitude,dist,table = BASE_TABLE ,columns = "*"):
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
        # TODO: return all the information we want
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
    return JsonResponse(hotels, status=200)


def search_places_by_point(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    latitude = request_json["latitude"]
    longitude = request_json["longitude"]
    distance = request_json["distance"]
    category = request_json["category"].lower()

    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, distance)

    query = 'SELECT * FROM places JOIN places_categories ON places.id = places_categories.place_id ' \
            'JOIN categories ON places_categories.category_id = categories.id WHERE categories.name = "' + category + \
            '" AND latitude BETWEEN ' + str(bottom) + ' AND ' + str(top) + ' AND ' \
            'longitude BETWEEN ' + str(left) + ' AND ' + str(right) + ' LIMIT 50'

    print "executing query : " + query

    places = dict()
    rows = execute_query(query)
    for result in rows:
        place = dict()
        place["id"] = result["id"]
        place["google_id"] = result["google_id"]
        place["name"] = result["name"]
        place["longitude"] = result["longitude"]
        place["latitude"] = result["latitude"]
        place["rating"] = result["rating"]
        place["vicinity"] = result["vicinity"]
        places[place["id"]] = place

    return JsonResponse(places, status=200)

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


def get_place_details(request, place_id):
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


#TODO: create the tables
def find_popular_search(places_id_list):
    #create an sql query to search if that search exists
    places_str = ""
    for i in range(len(places_id_list)):
        places_str  = places_str + " place_id = " + str(places_id_list[i]) + " AND "
    places_str = places_str[:-5] #remove the last add
    find_search_query = "SELECT search_id FROM searches_places WHERE" + places_str
    find_popular_query = "SELECT popularity FROM searches WHERE search_id = {" + find_search_query + "}"
    popularity_rate = execute_query(find_popular_query)
    #if it does, update
    if(popularity_rate > 0):
        return #TODO complete
    #else insert it
    else:
        return #TODO complete


def fetch_popular_routes():
    #this function will return our top searches.
    return


def calc_categories_statistics(request):
    if 'latitude' not in request.GET or 'longitude' not in request.GET or 'distance' not in request.GET:
        return JsonResponse(MISSING_QUERY_PARAMS, status=400)

    # get required query parameters latitude, longitude, distance
    latitude = request.GET['latitude']
    longitude = request.GET['longitude']
    distance = request.GET['distance']
    if not longitude or not latitude or not distance:
        return JsonResponse(INVALID_QUERY_PARAMS, status=400)

    top, right, bottom, left = get_boundaries_by_center_and_distance(longitude, latitude, distance)

    statistics = get_categories_statistics(top, right, bottom, left)

    return JsonResponse(statistics, status=200)

