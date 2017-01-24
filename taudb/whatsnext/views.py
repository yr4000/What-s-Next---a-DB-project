from __future__ import division
# Generic packages import
import json

# Django packages import
from django.shortcuts import render
from django.http import JsonResponse, Http404

# Internal packages import
from utils.db_utils import *
from utils.geo_utils import *
from utils.google_maps_access import fetch_reviews_rating_from_google
from utils.api_responses import MISSING_QUERY_PARAMS, INVALID_QUERY_PARAMS
from utils.exceptions import NotFoundInDb
from utils.data_access import get_place_by_place_id, get_place_reviews, get_categories_statistics, \
    search_places_near_location, search_places_by_name, lookup_choice_by_places_set, insert_new_choice, \
    update_choice, get_popular_places_for_category, crawl_by_location_highest_rating, get_popular_choices


def homepage(request):
    categories = []
    categories_results = execute_sfw_query("SELECT * FROM categories")
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

    places = search_places_by_name(search_word, search_category, page)

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
    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, distance)

    places = search_places_near_location(latitude, longitude, top, right, bottom, left, category, page)

    return JsonResponse(places, status=200)


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
        try:
            # fetch reviews for place from Google Places API, and store in db
            reviews, new_rating = fetch_reviews_rating_from_google(place=place)
        except:
            # invalid response from google - there are no reviews for this place
            reviews, new_rating = [], None

        # shows updated rating in case it was returned from Google
        if new_rating:
            place['rating'] = new_rating

    # convert reviews to dictionaries so they can be serialized
    reviews_dicts = list()
    for review in reviews:
        reviews_dicts.append(review.to_json())

    return JsonResponse({'place': place, 'reviews': reviews_dicts}, status=200)


def update_popular_search(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    places_id_list = request_json['places_id_list']

    choice_id = lookup_choice_by_places_set(places_id_list)

    # if there is not search like that, insert it to search_popularity and choices_places
    if choice_id:
        update_choice(choice_id)
        update_status = 'updated search popularity'
    else:
        insert_new_choice(places_id_list)
        update_status = 'inserted new search'
    return JsonResponse({'update_status': update_status}, status=200)


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


def calc_top_choices(request):
    top_choices = get_popular_choices()

    return JsonResponse(top_choices, status=200)


def calc_top_places_for_category(request):
    if 'category' not in request.GET:
        return JsonResponse(MISSING_QUERY_PARAMS, status=400)

    # get required query parameters
    category = request.GET['category']

    top_places = get_popular_places_for_category(category)

    return JsonResponse(top_places, status=200)


def im_feeling_lucky(request):
    if request.is_ajax() is False:
        raise Http404

    request_json = json.loads(request.body)

    latitude = request_json["latitude"]
    longitude = request_json["longitude"]
    distance = request_json["distance"]

    latitude, longitude = modify_longlat_for_db(latitude, longitude)
    top, right, bottom, left = get_boundaries_by_center_and_distance(latitude, longitude, distance)

    lucky_route = crawl_by_location_highest_rating(top, right, bottom, left)

    return JsonResponse(lucky_route, status=200)
