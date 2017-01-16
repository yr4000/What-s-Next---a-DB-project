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
    search_places_near_location, search_places_by_name, exe_find_search_id_query, insert_new_search, \
    update_search, get_popular_places_for_category, find_suggestion_near_location, exe_im_feeling_lucky_query


def homepage(request):
    categories = []
    categories_results = execute_SFW_query("SELECT * FROM categories")
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

    search_word = request_json["word"]
    search_category = request_json["category"].lower()
    page = request_json["page"]

    print "Searching for a " + search_category + " with " + search_word + \
          " in it's name [Page " + str(page) + "]"

    places = search_places_by_name(search_word, search_category, page)

    return JsonResponse(places, status=200)


def find_suggestion_by_point(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    latitude = request_json["latitude"]
    longitude = request_json["longitude"]
    page = request_json["page"]

    places = find_suggestion_near_location(latitude, longitude, page)

    return JsonResponse(places, status=200)


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
    page = request_json["page"]

    # modify the longitude and the latitude to be workable with DB.
    latitude, longitude = modify_longlat_for_db(latitude, longitude)

    #  returns a 4*distance**2 square around the selected point.
    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude,longitude, distance)

    places = search_places_near_location(latitude, longitude, top, right, bottom, left, category, page)

    return JsonResponse(places, status=200)


# returns a shortest pub crawl track from a starting point, according to number of bars
# pre: latitude and longitude are NOT modified
# TODO: consider save bar's name since there might be a couple of places in the same spot
def pub_crawl(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    latitude = 51.5363312, -0.0046230  # request_json["latitude"]
    longitude = 51.5363312, -0.0046230  # request_json["longitude"]
    num_of_bars = 4  # should be replaced later with len(categories)
    categories = request_json["categories"]

    track_points = [[0, 0, ""] for i in range(num_of_bars)]
    # initialize the first point in the track
    track_points[0][0], track_points[0][1], track_points[0][2] = latitude, longitude, "You are here"

    for i in range(1, num_of_bars):
        curr_min_dist = -1
        closest_point = [0, 0, ""]
        latitude,longitude = modify_longlat_for_db(latitude,longitude)
        # return all bars in range of 0.5 km
        top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, 0.5)
        # we don't want the same point to appear in the track twice
        exclude_lats = [track_points[x][0] for x in range(i)]
        exclude_longs = [track_points[x][1] for x in range(i)]
        # TODO: this query is for tests
        query = "SELECT latitude, longitude, name FROM places "\
                + " WHERE latitude <= " + str(top) \
                + " AND longitude <= " + str(right) \
                + " AND latitude >= " + str(bottom) \
                + " AND longitude >= " + str(left)

        # query = 'SELECT * FROM places JOIN places_categories ON places.id = places_categories.place_id ' \
        #         'JOIN categories ON places_categories.category_id = categories.id WHERE categories.name = "' + categories[i] + \
        #         '" AND latitude BETWEEN ' + str(bottom) + ' AND ' + str(top) + ' AND ' \
        #             'longitude BETWEEN ' + str(left) + ' AND ' + str(right) + ' LIMIT 50'
        # + " AND latitude NOT IN (" + exclude_lats[1:len(exclude_lats)-1]+")" \
        # + " AND longitude NOT IN (" + exclude_longs[1:len(exclude_longs)-1]+")"

        for x in range(i):
            query = query + " AND latitude != " + str(exclude_lats[x]) \
                            + " AND longitude != " + str(exclude_longs[x])
        rows = execute_SFW_query(query)
        if len(rows) == 0:
            break

        # for each point in range look for the closest one.
        # we save the min distance at curr_min_dist and it's point at closest_point
        for j in range(len(rows)):
            curr_point = (latitude, longitude)
            temp_p = (rows[j]["latitude"], rows[j]["longitude"],)
            temp_dist = gps_distance(curr_point, temp_p)
            if curr_min_dist == -1 or curr_min_dist > temp_dist:
                curr_min_dist = temp_dist
                closest_point[0] = rows[j]["latitude"]
                closest_point[1] = rows[j]["longitude"]
                closest_point[2] = rows[j]["name"]

        # add the current point to an array
        track_points[i][0] = closest_point[0]
        track_points[i][1] = closest_point[1]
        track_points[i][2] = closest_point[2]

        latitude, longitude = closest_point[0], closest_point[1]  # update the current point to be the closest we found
        # calculate again with the point found (returns to the start of the loop

    # TODO: print the points to map and a route if possible
    return HttpResponse(str(track_points))
    # return track_points


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

    # TODO: This does not use the Place class anymore, need to fix this
    return JsonResponse({'place': place, 'reviews': reviews_dicts}, status=200)


# TODO: should be called whenever a search is being made
def update_popular_search(request):

    update_status = ""

    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    places_id_list = request_json["places_id_list"]

    search_id = exe_find_search_id_query(places_id_list)
    # return JsonResponse({'update_status': update_status, 'search_is': len(search_id)}, status=200)

    # if there is not search like that, insert it to search_popularity and searches_places
    if len(search_id) == 0:
        insert_new_search(places_id_list)
        update_status += "inserted new search"
    elif len(search_id) > 1:
        return JsonResponse({'error': 'this search has more than one ID'}, status=404)
    else:
        update_search(search_id)
        update_status += "updated search"
    return JsonResponse({'update_status' : update_status}, status=200) #for debug


def calc_categories_statistics(request):
    if 'latitude' not in request.GET or 'longitude' not in request.GET or 'distance' not in request.GET:
        return JsonResponse(MISSING_QUERY_PARAMS, status=400)

    # get required query parameters
    latitude = float(request.GET['latitude'])
    longitude = float(request.GET['longitude'])
    distance = float(request.GET['distance'])
    # we want to return statistics for ALL categories EXCEPT the given category
    except_category = request.GET['except_category']

    # modify the longitude and the latitude to be workable with DB.
    latitude, longitude = modify_longlat_for_db(latitude, longitude)

    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, distance)

    statistics = get_categories_statistics(top, right, bottom, left, except_category)

    return JsonResponse(statistics, status=200)


def calc_top_places_for_category(request):
    if 'category' not in request.GET:
        return JsonResponse(MISSING_QUERY_PARAMS, status=400)

    # get required query parameters
    category = request.GET['category']

    top_places = get_popular_places_for_category(category)

    return JsonResponse(top_places, status=200)


#TODO: Yair finish
def im_feeling_lucky(latitude, longitude, distance):
    latitude, longitude = modify_longlat_for_db(latitude, longitude)
    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, distance)

    lucky_route = exe_im_feeling_lucky_query(top, right, bottom, left)