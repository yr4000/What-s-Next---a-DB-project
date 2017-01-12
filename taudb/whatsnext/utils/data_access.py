from db_utils import init_db_connection, init_db_cursor,execute_query
from whatsnext.models import Review, Place
from exceptions import NotFoundInDb
import MySQLdb as mdb
from taudb.settings import RESOLUTION,LONDON_LATITUDE_DB_CONST

DEFAULT_RESULTS_AMOUNT = 10


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


def find_suggestion_near_location(center_latitude, center_longitude):

    cur = init_db_cursor()

    query = 'Select 	                                                                                            ' \
            'p1.id As p1id,                                                                                         ' \
            '	p2id,                                                                                               ' \
            '	p3id,                                                                                               ' \
            '	p4id,                                                                                               ' \
            '	(sqrt((p4lat - %s)^2 / 10000 + (p4lon - %s)^2 / 10000) +                                            ' \
            '	sqrt((p3lat - p4lat)^2 / 10000 + (p3lon - p4lon)^2 / 10000) +                                       ' \
            '	sqrt((p2lat - p3lat)^2 / 10000 + (p2lon - p3lon)^2 / 10000) +                                       ' \
            '	sqrt((p1.latitude - p2lat)^2 / 10000 + (p1.longitude - p2lon)^2 / 10000)) As TotalDistAfterTransp   ' \
            'From                                                                                                   ' \
            '	places as p1,                                                                                       ' \
            '	places_categories as pc1,                                                                           ' \
            '	(Select                                                                                             ' \
            '		p2.id As p2id,                                                                                  ' \
            '	 	p3id,                                                                                           ' \
            '		p4id,                                                                                           ' \
            '		p2.latitude As p2lat,                                                                           ' \
            '		p2.longitude As p2lon,                                                                          ' \
            '       p4lat,                                                                                          ' \
            '		p4lon,                                                                                          ' \
            '		p3lat,                                                                                          ' \
            '		p3lon                                                                                           ' \
            '		From                                                                                            ' \
            '		places as p2,                                                                                   ' \
            '		places_categories as pc2,                                                                       ' \
            '		(Select                                                                                         ' \
            '			p4id,                                                                                       ' \
            '			p3.id As p3id,                                                                              ' \
            '			p3.latitude As p3lat,                                                                       ' \
            '			p3.longitude As p3lon,                                                                      ' \
            '			p4lat,                                                                                      ' \
            '			p4lon                                                                                       ' \
            '		From                                                                                            ' \
            '			places as p3,                                                                               ' \
            '			places_categories as pc3,                                                                   ' \
            '			(Select                                                                                     ' \
            '				p4.id As p4id,                                                                          ' \
            '				p4.latitude As p4lat,                                                                   ' \
            '               p4.longitude As p4lon                                                                   ' \
            '				From                                                                                    ' \
            '					places as p4,                                                                       ' \
            '					places_categories as pc4	                                                        ' \
            '			    Where                                                                                   ' \
            '					p4.id = pc4.place_id                                                                ' \
            '					And pc4.category_id = 4                                                             ' \
            '                   And p4.latitude BETWEEN %s - 15 AND %s + 15                                         ' \
            '                   AND p4.longitude BETWEEN %s - 5 AND %s + 5 ) AS muesums                             ' \
            '		Where                                                                                           ' \
            '			p3.id = pc3.place_id                                                                        ' \
            '			And pc3.category_id = 3                                                                     ' \
            '			And p3.latitude BETWEEN p4lat - 15 AND p4lat + 15                                           ' \
            'AND p3.longitude BETWEEN p4lon - 15 AND p4lat + 15 ) AS bars                                           ' \
            '	Where                                                                                               ' \
            '		p2.id = pc2.place_id                                                                            ' \
            '		And pc2.category_id = 2                                                                         ' \
            '		And p2.latitude BETWEEN p3lat - 15 AND p3lat + 15                                               ' \
            'AND p2.longitude BETWEEN p3lon - 15 AND p3lat + 15 ) AS resturants                                     ' \
            'Where                                                                                                  ' \
            '	p1.id = pc1.place_id                                                                                ' \
            '	And pc1.category_id = 1                                                                             ' \
            '	And p1.latitude BETWEEN p2lat - 15 AND p2lat + 15                                                   ' \
            '   AND p1.longitude BETWEEN p2lon - 15 AND p2lat + 15                                                  ' \
            'Order By                                                                                               ' \
            '	TotalDistAfterTransp'

    cur.execute(query, (center_longitude, center_longitude, center_latitude ,
                        center_latitude, center_longitude, center_longitude))
    rows = cur.fetchall()

    places = dict()
    for result in rows:
        place = query_results_to_dict(result)
        places[place["id"]] = place

    cur.close()

    return places

def search_places_near_location(center_latitude, center_longitude, top, right, bottom, left, category, limit):

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

    places = dict()
    for result in rows:
        place = query_results_to_dict(result)
        places[place["id"]] = place

    cur.close()

    return places


def query_results_to_dict(result):
    place = dict()
    place["id"] = result["id"]
    place["google_id"] = result["google_id"]
    place["name"] = result["name"]
    place["longitude"] = result["longitude"] / RESOLUTION
    place["latitude"] = (result["latitude"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST
    place["rating"] = result["rating"]
    place["vicinity"] = result["vicinity"]
    return place


def search_places_by_name(search_word, search_category, offset_for_paging):

    cur = init_db_cursor()

    # search by the word and the category
    query = 'SELECT                                                                            ' \
            '    full_text_results.id,                                                         ' \
            '    full_text_results.google_id,                                                  ' \
            '    full_text_results.name,                                                       ' \
            '    full_text_results.rating,                                                     ' \
            '    full_text_results.vicinity,                                                   ' \
            '    full_text_results.latitude,                                                   ' \
            '    full_text_results.longitude                                                   ' \
            'FROM                                                                              ' \
            '    (SELECT                                                                       ' \
            '        places.id,                                                                ' \
            '        places.google_id,                                                         ' \
            '        places.rating,                                                            ' \
            '        places.vicinity,                                                          ' \
            '        places.name,                                                              ' \
            '        places.latitude,                                                          ' \
            '        places.longitude                                                          ' \
            '    FROM                                                                          ' \
            '        places                                                                    ' \
            '    WHERE                                                                         ' \
            '        MATCH (places.name) AGAINST ("+%s" IN BOOLEAN MODE)) AS full_text_results ' \
            '        INNER JOIN                                                                ' \
            '    places_categories ON full_text_results.id = places_categories.place_id        ' \
            '        INNER JOIN                                                                ' \
            '    categories ON categories.id = places_categories.category_id                   ' \
            'WHERE                                                                             ' \
            '    categories.name = %s                                                          ' \
            'LIMIT %s, %s                                                                          '

    cur.execute(query, (search_word, search_category, offset_for_paging, DEFAULT_RESULTS_AMOUNT))

    rows = cur.fetchall()

    places = dict()
    for result in rows:
        place = query_results_to_dict(result)
        places[place["id"]] = place

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


def insert_new_reviews(reviews):
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


def update_place_rating(new_rating, place_id):
    if not new_rating or not place_id:
        raise ValueError('all arguments must be not None')

    # TODO: should use an object to obtain the connection and cursor
    conn = init_db_connection()
    cur = conn.cursor(mdb.cursors.DictCursor)

    query = 'UPDATE places   '\
            'SET             '\
            '    rating = %s '\
            'WHERE           '\
            '    id = %s     '

    # TODO: check what happens if review.date is None
    cur.execute(query, (new_rating, place_id))

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

    statistics = dict()
    for record in records:
        category_name = record['category_name']
        places_amount = record['places_amount']
        rating_average = record['rating_average']

        statistics[category_name] = {'places_amount': places_amount, 'rating_average': rating_average}

    cur.close()

    return statistics

# TODO: there should be a text box who autocomplete whenever the user starts a search
# TODO: create an sql query to search if that search exists
def find_popular_search(places_id_list):
    search_id = find_search_id_query(places_id_list)
    find_popular_query = "SELECT sp.popularity FROM ("+ search_id+ ") AS S_ID, search_popularity AS sp " \
                          "WHERE S_ID.search_id = sp.search_id"
    popularity_rate = execute_query(find_popular_query)
    return popularity_rate

#this function returns a string that determains which search_id will return.
#it is vital it returns a string and not execute anything.
def find_search_id_query(places_id_list):
    places_str = ""
    for place in places_id_list:
        places_str  += "place_id = " + str(place) + " AND "
    places_str += "search_size = " +str(len(places_id_list))
    return "SELECT search_id FROM searches_places WHERE " + places_str

def exe_find_search_id_query(places_id_list):
    return execute_query(find_search_id_query(places_id_list))

def insert_new_search(places_id_list):
    execute_query("INSERT INTO search_popularity(popularity) VALUES (1)")
    search_id = execute_query("SELECT MAX(search_id) FROM search_popularity")
    insert_to_searces_places = "INSERT INTO searches_places VALUES "
    for i in range(len(places_id_list)):
        insert_to_searces_places += "(" + str(search_id[0]["search_id"]) + "," + str(places_id_list[1]) + "), "
    execute_query(insert_to_searces_places[:-2])

def update_search(search_id):
    execute_query("UPDATE search_popularity SET popularity = popularity+1 WHERE search_id = " + str(search_id[0]["search_id"]))
