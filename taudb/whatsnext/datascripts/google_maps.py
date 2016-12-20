import urllib
import json
from london_coordinates import coordinates

KEY_NEXT_PAGE_TOKEN = 'next_page_token'
KEY_RESULTS = 'results'
KEY_PLACE_ID = 'place_id'
KEY_NAME = 'name'
KEY_PRICE_LEVEL = 'price_level'
KEY_RATING = 'rating'
KEY_VICINITY = 'vicinity'
KEY_GEOMETRY = 'geometry'
KEY_LOCATION = 'location'
KEY_LATITUDE = 'lat'
KEY_LONGITUDE = 'lng'

GOOGLE_API_KEY = 'AIzaSyCGnmhFJarg4hMWmtJF37V1NaINNXGpzBU'
HOST = 'https://maps.googleapis.com'
API = '/maps/api/place/search/json'


def run_google_maps():
    for latitude, longitude in coordinates:
        run_specific_coordinates(latitude=latitude, longitude=longitude)


def run_specific_coordinates(latitude, longitude):
    radius = 500
    place_type = 'lodging'
    next_page_token = None

    while True:
        print 'running iteration'
        # build the API request url
        url = '{host}{api}?key={api_key}&location={lat},{long}&radius={radius}&type={type}'.format(
            host=HOST,
            api_key=GOOGLE_API_KEY,
            api=API,
            lat=latitude,
            long=longitude,
            radius=radius,
            type=place_type)
        if next_page_token:
            url = '{base_url}&pagetoken={page_token}'.format(base_url=url, page_token=next_page_token)

        # process Google Places API response
        json_response = json.load(urllib.urlopen(url))

        if KEY_NEXT_PAGE_TOKEN in json_response:
            next_page_token = json_response[KEY_NEXT_PAGE_TOKEN]
        else:
            next_page_token = None

        # reduce to relevant data
        reduced_data = reduce_data(json_response)

        # write data to db
        write_data_to_db(reduced_data)

        # if response did not contain a next page - done with specific coordinates
        if not next_page_token:
            break


def write_data_to_db(data):
    # write data to db only if not empty
    if data:
        # TODO: currently this only appends to file
        with open('test.txt', 'a') as data_file:
            data_file.write('{data}'.format(data=data))


def reduce_data(json_response):
    reduced_places = list()

    # if response is empty or does not contain results return None
    if not json_response or KEY_RESULTS not in json_response:
        return reduced_places

    places = json_response[KEY_RESULTS]

    for place in places:
        reduced_place = dict()
        try:
            reduced_place[KEY_PLACE_ID] = str(place[KEY_PLACE_ID])
            reduced_place[KEY_NAME] = str(place[KEY_NAME])
            reduced_place[KEY_PRICE_LEVEL] = str(place[KEY_PRICE_LEVEL])
            reduced_place[KEY_RATING] = str(place[KEY_RATING])
            reduced_place[KEY_VICINITY] = str(place[KEY_VICINITY])
        except KeyError:
            # TODO: we do not want places with missing data in the db, but currently have no choice
            pass
            # continue

        reduced_places.append(reduced_place)

    return reduced_places


if __name__ == "__main__":
    run_google_maps()


# def byteify(input):
#     if isinstance(input, dict):
#         return {byteify(key): byteify(value)
#                 for key, value in input.iteritems()}
#     elif isinstance(input, list):
#         return [byteify(element) for element in input]
#     elif isinstance(input, unicode):
#         return input.encode('utf-8')
#     else:
#         return input
