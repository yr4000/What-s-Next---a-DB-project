import datetime
import json
import urllib
import thread

from django.conf import settings

from whatsnext.models import Review
from whatsnext.utils.data_access import insert_review_to_db

HOST = 'https://maps.googleapis.com'

KEY_RESULT = 'result'
KEY_REVIEWS = 'reviews'
KEY_AUTHOR_NAME = 'author_name'
KEY_RATING = 'rating'
KEY_TEXT = 'text'
KEY_TIME = 'time'


def fetch_reviews_from_google(place):
    url = '{host}{api}?key={api_key}&placeid={google_id}&language=en'.format(
        host=HOST,
        api_key=settings.GOOGLE_API_KEY,
        api='/maps/api/place/details/json',
        google_id=place.google_id)

    # process Google Places API response
    json_response = json.load(urllib.urlopen(url))
    check_response_status(json_response)

    new_reviews = convert_to_reviews_list(json_response, place.place_id)

    # insert_review_to_db(new_reviews)  # TODO: must be async, and grouped to a single insert query!
    try:
        thread.start_new_thread(insert_review_to_db, (new_reviews,))
    except Exception as e:
        print 'thread init failed. {}'.format(e.message)

    return new_reviews


def check_response_status(json_response):
    if 'status' not in json_response:
        raise Exception('got invalid response with no status')
    status = json_response['status']
    if status not in ('OK', 'ZERO_RESULTS'):
        raise Exception('response status was bad: {status}'.format(status=status))


# TODO: itzhaki also fetch the overall rating of the place to update it
def convert_to_reviews_list(json_response, place_id):
    new_reviews = list()

    # if response is empty or does not contain results return an empty list
    if not json_response or KEY_RESULT not in json_response:
        return new_reviews

    result = json_response[KEY_RESULT]
    if not result or KEY_REVIEWS not in result:
        return new_reviews

    reviews_raw_data = result[KEY_REVIEWS]

    for review_data in reviews_raw_data:
        # extract mandatory data
        try:
            author = review_data[KEY_AUTHOR_NAME]
            text = review_data[KEY_TEXT]
        except KeyError:
            continue

        # extract non-mandatory data
        try:
            rating = review_data[KEY_RATING]
        except KeyError:
            rating = 0
        try:
            timestamp = review_data[KEY_TIME]
            date = datetime.date.fromtimestamp(int(timestamp))
        except KeyError:
            date = None

        new_review = Review(review_id=None, place_id=place_id, author=author, rating=rating, text=text, date=date)

        new_reviews.append(new_review)

    return new_reviews
