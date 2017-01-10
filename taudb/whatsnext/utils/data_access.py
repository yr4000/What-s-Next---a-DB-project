from db_utils import init_db_connection, init_db_cursor
from whatsnext.models import Review, Place
from exceptions import NotFoundInDb
import MySQLdb as mdb
from taudb.settings import RESOLUTION


def get_place_by_place_id(place_id):
    if not place_id:
        raise ValueError('id argument must be not None')

    cur = init_db_cursor()

    query = 'SELECT                                                         '\
            '   places.id AS place_id,                                      '\
            '   places.google_id,                                           '\
            '   places.name,                                                '\
            '   places.rating,                                              '\
            '   places.vicinity,                                            '\
            '   places.latitude,                                            '\
            '   places.longitude,                                           '\
            '   categories.name AS category                                 '\
            'FROM                                                           '\
            '   places                                                      '\
            '       INNER JOIN                                              '\
            '   places_categories ON places.id = places_categories.place_id '\
            '       INNER JOIN                                              '\
            '   categories ON places_categories.category_id = categories.id '\
            'WHERE                                                          '\
            '   places.id = %s                                              '

    cur.execute(query, (place_id,))

    record = cur.fetchone()  # expecting single place since id is a pk
    if record:
        place = Place(**record)
    else:
        raise NotFoundInDb('db does not include a record with id: {id}'.format(id=id))

    cur.close()

    return place


def get_places_near_location(center_latitude, center_longitude, top, right, bottom, left, category, limit):

    cur = init_db_cursor()

    query = 'SELECT                                                                    '\
            '    places.id,                                                            '\
            '    places.google_id,                                                     '\
            '    places.name,                                                          '\
            '    places.longitude,                                                     '\
            '    places.latitude,                                                      '\
            '    places.rating,                                                        '\
            '    places.vicinity,                                                      '\
            '    (POWER((latitude - %s) , 2) + POWER((longitude - %s), 2)) AS distance '\
            'FROM                                                                      '\
            '    places                                                                '\
            '        JOIN                                                              '\
            '    places_categories ON places.id = places_categories.place_id           '\
            '        JOIN                                                              '\
            '    categories ON places_categories.category_id = categories.id           '\
            'WHERE                                                                     '\
            '    categories.name = %s                                                  '\
            '        AND latitude BETWEEN %s AND %s                                    '\
            '        AND longitude BETWEEN %s AND %s                                   '\
            'ORDER BY distance ASC                                                     '\
            'LIMIT %s                                                                  '

    # TODO: why do we have a limit set from the client? why do we have a limit at all?
    # TODO: this could easily become a more complicated query and be part of the required 6 (it's currently not!)
    cur.execute(query, (center_latitude, center_longitude, category, bottom, top, left, right, limit))
    rows = cur.fetchall()

    # TODO: this is not a good structure of the json, but it's not critical if we don't have time.
    places = dict()
    for result in rows:
        place = dict()
        place["id"] = result["id"]
        place["google_id"] = result["google_id"]
        place["name"] = result["name"]
        place["longitude"] = result["longitude"] / RESOLUTION
        place["latitude"] = (result["latitude"] / RESOLUTION) + 51
        place["rating"] = result["rating"]
        place["vicinity"] = result["vicinity"]
        places[place["id"]] = place

    cur.close()

    return places


def get_place_reviews(place):
    if not place:
        raise ValueError('place argument must be not None')

    cur = init_db_cursor()

    query = 'SELECT                      '\
            '   reviews.id as review_id, '\
            '   reviews.place_id,        '\
            '   reviews.author,          '\
            '   reviews.rating,          '\
            '   reviews.text,            '\
            '   reviews.date             '\
            'FROM                        '\
            '   reviews                  '\
            'WHERE                       '\
            '   reviews.place_id = %s    '

    cur.execute(query, (place.place_id,))

    records = cur.fetchall()

    reviews = list()
    for record in records:
        review = Review(**record)
        reviews.append(review)

    cur.close()

    return reviews


def insert_review_to_db(reviews):
    if not reviews:
        raise ValueError('reviews argument must be not None')

    # convert the reviews list to a list of tuples, so it can be used in the query execution
    reviews_tuples_list = list()
    for review in reviews:
        reviews_tuples_list.append((review.place_id, review.author, review.rating, review.text, review.date))

    # TODO: should use an object to obtain the connection and cursor
    conn = init_db_connection()
    cur = conn.cursor(mdb.cursors.DictCursor)

    query = 'INSERT INTO reviews (`place_id`, `author`, `rating`, `text`, `date`) '\
            'VALUES (%s, %s, %s, %s, %s)                                          '

    # TODO: check what happens if review.date is None
    cur.executemany(query, reviews_tuples_list)

    conn.commit()

    cur.close()


def get_categories_statistics(top, right, bottom, left):
    if not top or not right or not bottom or not left:
        raise ValueError('location arguments must be not None')

    cur = init_db_cursor()

    query = 'SELECT                                                                ' \
            '    categories.name AS category_name,                                 ' \
            '    COUNT(places.id) AS places_amount,                                ' \
            '    ROUND(AVG(places_rated.rating), 2) AS rating_average              ' \
            'FROM                                                                  ' \
            '    places                                                            ' \
            '        JOIN                                                          ' \
            '    places_categories ON places.id = places_categories.place_id       ' \
            '        JOIN                                                          ' \
            '    categories ON places_categories.category_id = categories.id       ' \
            '        JOIN                                                          ' \
            '    (SELECT                                                           ' \
            '        places.id, places.rating                                      ' \
            '    FROM                                                              ' \
            '        places                                                        ' \
            '    WHERE                                                             ' \
            '        rating > 0) AS places_rated ON places.id = places_rated.id    ' \
            'WHERE                                                                 ' \
            '    latitude BETWEEN %s AND %s                                        ' \
            '        AND longitude BETWEEN %s AND %s                               ' \
            'GROUP BY categories.name                                              ' \
            'HAVING places_amount > 0;                                             '

    cur.execute(query, (bottom, top, left, right))

    records = cur.fetchall()

    statistics = list()
    for record in records:
        category_name = record['category_name']
        place_amount = record['place_amount']
        rating_average = record['rating_average']

        statistics.append({'category_name': category_name,
                           'place_amount': place_amount,
                           'rating_average': rating_average})

    cur.close()

    return statistics


def find_search_id_query(places_id_list):
    places_str = ""
    for place in places_id_list:
        places_str  += "place_id = " + str(place) + " AND "
    places_str += "search_size = " +str(len(pl)) #remove the last add
    return "SELECT search_id FROM searches_places WHERE " + places_str


