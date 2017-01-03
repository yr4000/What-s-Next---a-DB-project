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
KEY_RATING = 'rating'
KEY_VICINITY = 'vicinity'
KEY_GEOMETRY = 'geometry'
KEY_LOCATION = 'location'
KEY_LATITUDE = 'lat'
KEY_LONGITUDE = 'lng'

GOOGLE_API_KEY = 'AIzaSyCGnmhFJarg4hMWmtJF37V1NaINNXGpzBU'
HOST = 'https://maps.googleapis.com'
API = '/maps/api/place/search/json'

# TAU DB
conn = mdb.connect(host='127.0.0.1', port=11211, user='DbMysql06', passwd='DbMysql06', db='DbMysql06')

# LOCAL DB
# conn = mdb.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='taudb')

category_mapping = {'lodging': '1',
                    'restaurant': '2',
                    'bar': '3',
                    'museum': '4'}


def run_google_maps_migration():
    for latitude, longitude in coordinates:
        run_specific_coordinates(latitude=latitude, longitude=longitude)


def run_specific_coordinates(latitude, longitude):
    print 'starting with coordinates: {lat},{long}'.format(lat=latitude, long=longitude)

    radius = 1000
    place_type = 'museum'
    next_page_token = None
    places_added_total = 0
    mappings_added_total = 0

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
            places_added, mappings_added = write_data_to_db(place=place, category=place_type)
            places_added_total = places_added_total + places_added
            mappings_added_total = mappings_added_total + mappings_added

        print 'done writing data to db'

        # must have at least 2 seconds interval between API calls
        sleep(3)

        # if response did not contain a next page - done with specific coordinates
        if not next_page_token:
            print 'next page token empty - breaking out of loop'
            break

    print 'done with coordinates: {lat},{long}. added {num_p} places and {num_m} mappings'.format(
        lat=latitude, long=longitude, num_p=places_added_total, num_m=mappings_added_total)
    print


def write_data_to_db(place, category):
    places_added = 0
    mappings_added = 0

    # write data to db only if not empty
    if not place:
        return places_added, mappings_added

    cur = conn.cursor(mdb.cursors.DictCursor)
    try:
        # add a new place to db
        places_added = cur.execute(
            'insert into places (`google_id`, `name`, `rating`, `vicinity`, `latitude`, `longitude`) '
            'values (%s, %s, %s, %s, %s, %s)',
            (place.google_id, place.name, place.rating, place.vicinity, place.latitude, place.longitude))

        conn.commit()

        # get the id of the newly inserted place
        place.id = cur.lastrowid
    except mdb.IntegrityError:
        print 'failed to insert new place with google_id {id}. reason: already exists in places table'.format(
            id=place.google_id)
        # get the id of the place with this current id, to map its category later
        cur.execute('select id from places where google_id = %s', (place.google_id,))
        place.id = cur.fetchone()['id']

    try:
        # map the place (could be either old or new) to current category
        mappings_added = cur.execute('insert into places_categories (`place_id`, `category_id`) values (%s, %s)',
                                     (place.id, category_mapping[category]))

        conn.commit()
    except mdb.IntegrityError:
        print 'failed to map place with id {id} to category {category}. reason: already exists db'.format(
            id=place.google_id, category=category_mapping[category])

    cur.close()
    return places_added, mappings_added


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
