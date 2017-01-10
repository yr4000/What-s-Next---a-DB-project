from __future__ import division
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
from utils.data_access import get_place_by_place_id, get_place_reviews, get_categories_statistics, \
    get_places_near_location, find_search_id_query

# Globals
BARS_VIEW = "places"  # TODO replace when time comes
BASE_TABLE = "places_v2"


def homepage(request):
    categories = []
    categories_results = execute_query("SELECT * FROM categories")
    for category in categories_results:
        categories.append(category["name"].capitalize())

    contexts = {
        'categories': categories
    }
    return render(request, 'whatsnext/index.html', context=contexts)


def search_by_name(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    places = dict()

    categories = ['Lodging', 'Bar', 'Restaurant', 'Museum']

    word_to_search = request_json["word"]
    category_for_search = request_json["category"]
    limit_for_query = request_json["limit"]

    cur = init_db_cursor()

    # Get places whom contain the word in the request
    if category_for_search in categories:
        # search by the word and by the category also
        query = 'Select full_text_results.id, full_text_results.google_id, full_text_results.name, ' \
                'full_text_results.rating, full_text_results.vicinity, ' \
                'full_text_results.latitude, full_text_results.longitude ' \
                'From (Select * From places_v2 ' \
                '      Where Match(places_v2.name) ' \
                '      Against("+%s" in boolean mode)) As full_text_results ' \
                'Inner join places_categories ON full_text_results.id = places_categories.place_id ' \
                'Inner join categories ON categories.id = places_categories.category_id ' \
                'Where categories.name = %s' \
                'LIMIT %s'
        cur.execute(query, (word_to_search, category_for_search, limit_for_query))
    else:
        # search only by the word
        query = 'Select * From places_v2 ' \
                'Where Match(places_v2.name) ' \
                'Against("+%s" in boolean mode)'
        cur.execute(query, (word_to_search, ))

    rows = cur.fetchall()
    for row in rows:
        place = dict()
        place["id"] = row["id"]
        place["google_id"] = row["google_id"]
        place["rating"] = row["rating"]
        place["vicinity"] = row["vicinity"]
        place["name"] = row["name"]
        place["latitude"] = (row["latitude"] / 10000.0) + 51
        place["longitude"] = (row["longitude"] / 10000.0)
        places[row["id"]] = place

    return JsonResponse(places, status=201)


# input : latitude, longitude, distance, category
# output : a square sized distance**2 with all the places from that category in it's range
def search_places_by_point(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    latitude = request_json["latitude"]
    longitude = request_json["longitude"]
    distance = request_json["distance"]
    category = request_json["category"].lower()
    limit = request_json["limit"]

    #  returns a 4*distance**2 square around the selected point.
    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, distance)

    places = get_places_near_location(latitude, longitude, top, right, bottom, left, category, limit)

    return JsonResponse(places, status=200)


'''
 returns a shortest pub crawl track from a starting point, according to number of bars
 pre: latitude and longitude are NOT modified
'''
# TODO: consider save bar's name since there might be a couple of places in the same spot
def pub_crawl(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    latitude = 51.5363312,-0.0046230 #request_json["latitude"]
    longitude = 51.5363312,-0.0046230 #request_json["longitude"]
    numOfBars = 4 #should be replaced later with len(categories)
    categories = request_json["categories"]

    trackPoints = [[0, 0,""] for i in range(numOfBars)]
    trackPoints[0][0], trackPoints[0][1], trackPoints[0][2] = latitude, longitude, "You are here" # initialize the first point in the track

    for i in range(1,numOfBars):
        currMinDist = -1
        closestPoint = [0, 0,""]
        # return all bars in range of 0.5 km
        top, right, bottom, left = get_boundaries_by_center_and_distance(latitude,longitude,0.5)
        excludeLats = [trackPoints[x][0] for x in range(i)]  # we don't want the same point to appear in the track twice
        excludeLongs = [trackPoints[x][1] for x in range(i)]
        #TODO this query is for tests
        query = "SELECT latitude, longitude, name FROM " + BARS_VIEW \
                + " WHERE latitude <= " + str(top) \
                + " AND longitude <= " + str(right) \
                + " AND latitude >= " + str(bottom) \
                + " AND longitude >= " + str(left)
        '''
        query = 'SELECT * FROM places JOIN places_categories ON places.id = places_categories.place_id ' \
                'JOIN categories ON places_categories.category_id = categories.id WHERE categories.name = "' + categories[i] + \
                '" AND latitude BETWEEN ' + str(bottom) + ' AND ' + str(top) + ' AND ' \
                    'longitude BETWEEN ' + str(left) + ' AND ' + str(right) + ' LIMIT 50'
        '''
                #+ " AND latitude NOT IN (" + excludeLats[1:len(excludeLats)-1]+")" \
                #+ " AND longitude NOT IN (" + excludeLongs[1:len(excludeLongs)-1]+")"
        for x in range(i):
            query = query + " AND latitude != " + str(excludeLats[x]) \
                            + " AND longitude != " + str(excludeLongs[x])
        rows = execute_query(query)
        if len(rows) == 0:
            break

        # for each point in range look for the closest one.
        # we save the min distance at currMinDist and it's point at closestPoint
        for j in range(len(rows)):
            currPoint = (latitude,longitude)
            tempP = (rows[j]["latitude"],rows[j]["longitude"],)
            tempDist = gps_distance(currPoint,tempP)
            if currMinDist == -1 or currMinDist > tempDist:
                currMinDist = tempDist
                closestPoint[0], closestPoint[1], closestPoint[2] = rows[j]["latitude"], rows[j]["longitude"], rows[j]["name"]
        # add the current point to an array
        trackPoints[i][0], trackPoints[i][1], trackPoints[i][2] = closestPoint[0], closestPoint[1], closestPoint[2]
        latitude, longitude = closestPoint[0] , closestPoint[1]  # update the current point to be the closest we found
        # calculate again with the point found (returns to the start of the loop

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


#TODO there should be a text box who autocomplete whenever the user starts a search
#create an sql query to search if that search exists
def find_popular_search(places_id_list):
    search_id = find_search_id_query(places_id_list)
    find_popular_query = "SELECT sp.popularity FROM ("+ search_id+ ") AS S_ID, search_popularity AS sp " \
                          "WHERE S_ID.search_id = sp.search_id"
    popularity_rate = execute_query(find_popular_query)
    return popularity_rate


#TODO should be called whenever a search is being made
def update_popular_search(places_id_list):
    search_id = execute_query(find_search_id_query(places_id_list))
    # if there is not search like that, insert it to search_popularity and searches_places
    if not search_id:
        execute_query("INSERT INTO search_popularity(popularity) VALUES (1)")
        search_id = execute_query("SELECT MAX(search_id) FROM search_popularity")
        insert_to_searces_places = "INSERT INTO searches_places VALUES "
        for i in range(len(places_id_list)):
            insert_to_searces_places += "("+str(search_id[0]["search_id"])+","+str(places_id_list[1])+"), "
        execute_query(insert_to_searces_places[:-2])

    elif(len(search_id)>1):
        return JsonResponse({'error': 'this search has more than one ID'}, status=404)

    else:
        execute_query("UPDATE search_popularity SET popularity = popularity+1 WHERE search_id = " +str(search_id[0]["search_id"]))
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

