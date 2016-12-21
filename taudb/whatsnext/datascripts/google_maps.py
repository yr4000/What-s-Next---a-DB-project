import urllib
import json
from london_coordinates import coordinates
import MySQLdb as mdb
from taudb.whatsnext.models.place import Place
from time import sleep

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

conn = mdb.connect('localhost', 'root', '', 'taudb')


def run_google_maps_migration():
    for latitude, longitude in coordinates:
        run_specific_coordinates(latitude=latitude, longitude=longitude)


def run_specific_coordinates(latitude, longitude):
    print 'starting with coordinates: {lat},{long}'.format(lat=latitude, long=longitude)

    radius = 1000
    place_type = 'lodging'
    next_page_token = None
    rows_added = 0

    while True:
        print 'starting new request iteration'
        # build the API request url
        base_url = '{host}{api}?key={api_key}'.format(
            host=HOST,
            api_key=GOOGLE_API_KEY,
            api=API)
        if next_page_token:
            url = '{base_url}&pagetoken={page_token}'.format(base_url=base_url, page_token=next_page_token)
        else:
            url = '{base_url}&location={lat},{long}&radius={radius}&type={type}'.format(
                base_url=base_url,
                lat=latitude,
                long=longitude,
                radius=radius,
                type=place_type)

        # process Google Places API response
        json_response = json.load(urllib.urlopen(url))

        if KEY_NEXT_PAGE_TOKEN in json_response:
            next_page_token = json_response[KEY_NEXT_PAGE_TOKEN]
        else:
            next_page_token = None

        # convert response to places list
        new_places = convert_to_places_list(json_response)

        # write new place to db
        for place in new_places:
            rows_added = rows_added + write_data_to_db(place)

        print 'done writing data to db'

        # must have at least 2 seconds interval between API calls
        sleep(3)

        # if response did not contain a next page - done with specific coordinates
        if not next_page_token:
            print 'next page token empty - breaking out of loop'
            break

    print 'done with coordinates: {lat},{long}. added {num} rows'.format(lat=latitude, long=longitude, num=rows_added)
    print


def write_data_to_db(place):
    rows_affected = 0

    # write data to db only if not empty
    if not place:
        return rows_affected

    cur = conn.cursor(mdb.cursors.DictCursor)

    rows_affected = cur.execute(
        'insert into places (`google_id`, `name`, `rating`, `vicinity`, `latitude`, `longitude`) '
        'values (%s, %s, %s, %s, %s, %s)',
        (place.google_id, place.name, place.rating, place.vicinity, place.latitude, place.longitude))

    conn.commit()
    cur.close()

    return rows_affected


def convert_to_places_list(json_response):
    new_places = list()

    # if response is empty or does not contain results return None
    if not json_response or KEY_RESULTS not in json_response:
        return new_places

    places = json_response[KEY_RESULTS]

    for place in places:
        # new_place = None

        # extract mandatory data
        try:
            google_id = place[KEY_PLACE_ID]
            name = place[KEY_NAME]
            latitude = place[KEY_GEOMETRY][KEY_LOCATION][KEY_LATITUDE]
            longitude = place[KEY_GEOMETRY][KEY_LOCATION][KEY_LONGITUDE]
        except KeyError:
            continue

        # extract non-mandatory data
        try:
            rating = place[KEY_RATING]
        except KeyError:
            rating = 0

        try:
            vicinity = place[KEY_VICINITY]
        except KeyError:
            vicinity = None

        new_place = Place(id=None, google_id=google_id, name=name, rating=rating,
                          vicinity=vicinity, latitude=latitude, longitude=longitude)

        new_places.append(new_place)

    return new_places


if __name__ == "__main__":
    run_google_maps_migration()
    conn.close()
