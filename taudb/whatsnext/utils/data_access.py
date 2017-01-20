from db_utils import init_db_connection, init_db_cursor,execute_sfw_query,execute_writing_query
from whatsnext.models import Review, Place
from exceptions import NotFoundInDb
import MySQLdb as mdb
from geo_utils import RESOLUTION,LONDON_LATITUDE_DB_CONST

import json
from django.http import HttpResponse, JsonResponse, Http404

DEFAULT_RESULTS_AMOUNT = 10


def get_place_by_place_id(place_id):
    if not place_id:
        raise ValueError('id argument must be not None')

    cur = init_db_cursor()

    query = 'SELECT                                                         '\
            '   places.id,                                                  '\
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
        place = query_results_to_dict(record)
    else:
        raise NotFoundInDb('db does not include a record with id: {id}'.format(id=id))

    cur.close()

    return place


def search_places_near_location(center_latitude, center_longitude, top, right, bottom, left, category, page):

    cur = init_db_cursor()

    # This query gets places inside the square surrounding the location specified by center_latitude, center_longitude
    # Also, only places with proper category are included in the result set
    # The results are ordered by the distance of each place from the center
    # To enable pagination, the result set is determined by a limit and an offset sent by caller
    query = 'SELECT                                                                    '\
            '    places.id,                                                            '\
            '    places.google_id,                                                     '\
            '    places.name,                                                          '\
            '    places.longitude,                                                     '\
            '    places.latitude,                                                      '\
            '    places.rating,                                                        '\
            '    places.vicinity,                                                      '\
            '    categories.name AS category,                                          '\
            '    (POWER((latitude - %s) , 2) + POWER((longitude - %s), 2)) AS distance '\
            'FROM                                                                      '\
            '    places                                                                '\
            '        JOIN                                                              '\
            '    places_categories ON places.id = places_categories.place_id           '\
            '        JOIN                                                              '\
            '    categories ON places_categories.category_id = categories.id           '\
            'WHERE                                                                     '\
            '    categories.name = %s                                                  '\
            '    AND latitude BETWEEN %s AND %s                                        '\
            '    AND longitude BETWEEN %s AND %s                                       '\
            'ORDER BY distance ASC                                                     '\
            'LIMIT %s, %s                                                              '

    # TODO: this could easily become a more complicated query and be part of the required 6 (it's currently not!)
    cur.execute(query, (center_latitude, center_longitude, category, bottom, top, left, right,
                        page * DEFAULT_RESULTS_AMOUNT, DEFAULT_RESULTS_AMOUNT))
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
    place["category"] = result["category"]
    return place


def search_places_by_name(search_word, search_category, page):

    cur = init_db_cursor()

    # This query gets places with proper category and names matching given search_word, using boolean mode text search
    # The results are then ordered by relevance, based the relevance score of match + against
    # To enable pagination, the result set is determined by a limit and an offset sent by caller
    query = 'SELECT                                                                 ' \
            '   places.id,                                                          ' \
            '   places.google_id,                                                   ' \
            '   places.rating,                                                      ' \
            '   places.vicinity,                                                    ' \
            '   places.name,                                                        ' \
            '   places.latitude,                                                    ' \
            '   places.longitude,                                                   ' \
            '   categories.name AS category,                                        ' \
            '   MATCH (places.name) AGAINST ("%s") AS relevance                     ' \
            'FROM                                                                   ' \
            '   places                                                              ' \
            '      INNER JOIN                                                       ' \
            '   places_categories ON places.id = places_categories.place_id         ' \
            '      INNER JOIN                                                       ' \
            '   categories ON categories.id = places_categories.category_id         ' \
            'WHERE                                                                  ' \
            '   MATCH (places.name) AGAINST ("%s" IN boolean mode)                  ' \
            '   AND categories.name = %s                                            ' \
            'HAVING                                                                 ' \
            '   relevance > 0                                                       ' \
            'ORDER BY                                                               ' \
            '   relevance DESC                                                      ' \
            'LIMIT %s, %s                                                           '

    cur.execute(query, (search_word, search_word, search_category, page * DEFAULT_RESULTS_AMOUNT,
                        DEFAULT_RESULTS_AMOUNT))

    rows = cur.fetchall()

    print "fullTextSearch returning " + str(len(rows)) + " results"

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

    # cur.execute(query, (place.place_id,)) TODO: this does not use the Place class anymore, need to fix this
    cur.execute(query, (place['id'],))

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

    try:
        # TODO: check what happens if review.date is None
        cur.executemany(query, reviews_tuples_list)
        conn.commit()
    except:
        conn.rollback()

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

    try:
        # TODO: check what happens if review.date is None
        cur.execute(query, (new_rating, place_id))
        conn.commit()
    except:
        conn.rollback()

    cur.close()


def get_categories_statistics(top, right, bottom, left, except_category):
    if not top or not right or not bottom or not left:
        raise ValueError('location arguments must be not None')

    cur = init_db_cursor()

    # This query gets statistics on all categories except a specific category sent by caller
    # The first statistic is amount of places for each category surrounding a given location
    # The second statistic is the average rating for each category surrounding a given location, excluding 0 ratings
    query = 'SELECT                                                                ' \
            '    categories.name AS category_name,                                 ' \
            '    COUNT(places.id) AS places_amount,                                ' \
            '    ROUND(AVG(places_rated.rating), 2) AS rating_average              ' \
            'FROM                                                                  ' \
            '    places                                                            ' \
            '        INNER JOIN                                                    ' \
            '    places_categories ON places.id = places_categories.place_id       ' \
            '        INNER JOIN                                                    ' \
            '    categories ON places_categories.category_id = categories.id       ' \
            '        LEFT JOIN                                                     ' \
            '    (SELECT                                                           ' \
            '        places.id, places.rating                                      ' \
            '    FROM                                                              ' \
            '        places                                                        ' \
            '    WHERE                                                             ' \
            '        rating > 0) AS places_rated ON places.id = places_rated.id    ' \
            'WHERE                                                                 ' \
            '   latitude BETWEEN %s AND %s                                         ' \
            '        AND longitude BETWEEN %s AND %s                               ' \
            'GROUP BY categories.name                                              ' \
            'HAVING places_amount > 0 AND categories.name != %s                    '

    cur.execute(query, (bottom, top, left, right, except_category))

    records = cur.fetchall()

    statistics = dict()
    for record in records:
        category_name = record['category_name']
        places_amount = record['places_amount']
        rating_average = record['rating_average']

        statistics[category_name] = {'places_amount': places_amount, 'rating_average': rating_average}

    cur.close()

    return statistics


def get_popular_places_for_category(category):
    if not category:
        raise ValueError('category argument must be not None')

    cur = init_db_cursor()

    # This query dynamically calculates places popularity on a scale of 1 to 5 according to the following formula:
    #       4 * ((x - min_p) / (max_p - min_p)) + 1
    # where:
    #       x       = current place popularity
    #       min_p   = minimal popularity (while ignoring 0 as a possible value, i.e: ignoring places not chosen at all)
    #       max_p   = maximal popularity
    # Meaning, this formula scales values to a range of 1-5 without assumptions on raw min and max popular values
    # Result set includes the top 5 chosen places in the specific category sent by caller
    query = 'SELECT places.id,                                                                          '\
            '       places.name,                                                                        '\
            '       places.google_id,                                                                   '\
            '       places.rating,                                                                      '\
            '       places.vicinity,                                                                    '\
            '       places.latitude,                                                                    '\
            '       places.longitude,                                                                   '\
            '       categories.name AS category,                                                        '\
            '       ROUND((4 * ( ( Sum(choices.popularity) -                                            '\
            '               extreme_popularities.min_raw_popularity ) /                                 '\
            '               (                                                                           '\
            '                   extreme_popularities.max_raw_popularity -                               '\
            '                   extreme_popularities.min_raw_popularity ) ) + 1), 2) as popularity      '\
            'FROM   (places                                                                             '\
            '        INNER JOIN choices_places                                                          '\
            '                ON places.id = choices_places.place_id                                     '\
            '        INNER JOIN choices                                                                 '\
            '                ON choices_places.choice_id = choices.choice_id                            '\
            '        INNER JOIN places_categories                                                       '\
            '                ON places.id = places_categories.place_id                                  '\
            '        INNER JOIN categories                                                              '\
            '                ON places_categories.category_id = categories.id),                         '\
            '       (SELECT Max(raw_popularity) AS max_raw_popularity,                                  '\
            '               Min(raw_popularity) AS min_raw_popularity                                   '\
            '        FROM   (SELECT places.id                         AS place_id,                      '\
            '                       Sum(choices.popularity) AS raw_popularity                           '\
            '                FROM   places                                                              '\
            '                       INNER JOIN choices_places                                           '\
            '                               ON places.id = choices_places.place_id                      '\
            '                       INNER JOIN choices                                                  '\
            '                               ON choices_places.choice_id =  choices.choice_id            '\
            '                       INNER JOIN places_categories                                        '\
            '                               ON places.id = places_categories.place_id                   '\
            '                       INNER JOIN categories                                               '\
            '                               ON places_categories.category_id = categories.id            '\
            '                WHERE  categories.name = %s                                                '\
            '                GROUP  BY places.id) AS raw_popularities) AS extreme_popularities          '\
            'WHERE  categories.name = %s                                                                '\
            'GROUP  BY places.id,                                                                       '\
            '          places.name                                                                      '\
            'ORDER  BY popularity DESC                                                                  '\
            'LIMIT 5                                                                                    '

    cur.execute(query, (category, category))

    records = cur.fetchall()

    top_places = dict()
    for record in records:
        place_dict = query_results_to_dict(record)
        place_dict['popularity'] = record['popularity']

        top_places[place_dict['id']] = place_dict

    cur.close()

    return top_places


def get_popular_choices():
    cur = init_db_cursor()

    # This query dynamically calculates top choices popularity on a scale of 1 to 5 according to the following formula:
    #       4 * ((x - min_p) / (max_p - min_p)) + 1
    # where:
    #       x       = current place popularity
    #       min_p   = minimal popularity (while ignoring 0 as a possible value, i.e: ignoring places not chosen at all)
    #       max_p   = maximal popularity
    # Meaning, this formula scales values to a range of 1-5 without assumptions on raw min and max popular values
    # Result set includes the places included in the top 5 chosen sets of places 
    query = 'SELECT places.id,                                                            '\
            '       places.google_id,                                                     '\
            '       places.name,                                                          '\
            '       places.vicinity,                                                      '\
            '       places.rating,                                                        '\
            '       places.latitude,                                                      '\
            '       places.longitude,                                                     '\
            '       categories.name AS category,                                          '\
            '       top_choices.choice_id,                                                '\
            '       top_choices.popularity                                                '\
            'FROM   (SELECT choice_id,                                                    '\
            '               Round(( 4 * ( ( popularity - min_raw_popularity ) / (         '\
            '                                     max_raw_popularity - min_raw_popularity '\
            '                                       ) ) + 1 ), 2) AS popularity           '\
            '        FROM   choices,                                                      '\
            '               (SELECT Max(popularity) AS max_raw_popularity                 '\
            '                FROM   choices) AS max_popularity,                           '\
            '               (SELECT Min(popularity) AS min_raw_popularity                 '\
            '                FROM   choices) AS min_popularity                            '\
            '        ORDER  BY popularity DESC                                            '\
            '        LIMIT  5) AS top_choices                                             '\
            '       INNER JOIN choices_places                                             '\
            '               ON top_choices.choice_id = choices_places.choice_id           '\
            '       INNER JOIN places                                                     '\
            '               ON choices_places.place_id = places.id                        '\
            '       INNER JOIN places_categories                                          '\
            '               ON places.id = places_categories.place_id                     '\
            '       INNER JOIN categories                                                 '\
            '               ON places_categories.category_id = categories.id              '\
            'ORDER  BY top_choices.popularity DESC,                                       '\
            '          top_choices.choice_id DESC;                                        '

    cur.execute(query)

    records = cur.fetchall()

    top_choices = dict()
    for record in records:
        place = dict()
        place['id'] = record['id']
        place['google_id'] = record['google_id']
        place['name'] = record['name']
        place['longitude'] = record['longitude'] / RESOLUTION
        place['latitude'] = (record['latitude'] / RESOLUTION) + LONDON_LATITUDE_DB_CONST
        place['rating'] = record['rating']
        place['vicinity'] = record['vicinity']
        place['category'] = record['category']
        choice_id = record['choice_id']
        popularity = record['popularity']

        if choice_id in top_choices:
            existing_choice = top_choices[choice_id]
            choice_places = existing_choice['choice_places']
            choice_places[place['id']] = place
        else:
            choice_places = dict()
            choice_places[place['id']] = place
            top_choices[choice_id] = {
                'choice_id': choice_id,
                'popularity': popularity,
                'choice_places': choice_places
            }

    cur.close()
    return top_choices


def lookup_choice_by_places_set(places_ids_list):
    if not places_ids_list:
        raise ValueError('places_ids_list argument must be not None nor empty')

    # create a sorted string of the ids, joined with a space separator
    places_ids_str = ' '.join([str(place_id) for place_id in sorted(places_ids_list)])

    cur = init_db_cursor()

    # This query returns the single choice_id, if exists, that includes the exact same set of places sent from caller.
    # The argument places_ids_str is a str containing the relevant set of places, ordered ascending by place_id,
    # to allow checking string equality with the sorted group of places for each choice from db.
    query = 'SELECT                                                                    '\
            '    lookup_results.choice_id                                              '\
            'FROM                                                                      '\
            '    (SELECT                                                               '\
            '        IF(%s = GROUP_CONCAT(place_id ORDER BY place_id SEPARATOR \' \'), '\
            '            choice_id,                                                    '\
            '            - 1) AS choice_id                                             '\
            '    FROM                                                                  '\
            '        choices_places                                                    '\
            '    GROUP BY choice_id) AS lookup_results                                 '\
            'WHERE                                                                     '\
            '    lookup_results.choice_id >= 0;                                        '

    cur.execute(query, (places_ids_str, ))

    if cur.rowcount > 0:
        record = cur.fetchone()  # expecting a single record because of the "group by choice_id" in the query
        choice_id = record['choice_id']
    else:
        choice_id = None

    cur.close()
    return choice_id


def insert_new_choice(places_ids_list):

    conn = init_db_connection()
    cur = conn.cursor(mdb.cursors.DictCursor)

    try:
        # insert a new choice with the initial popularity=1, and get the new choice_id
        choice_query = 'INSERT INTO choices (`popularity`) VALUES (1)'
        cur.execute(choice_query)

        # use the new choice_id and the parameter places_ids_list to build the arguments for next insert
        choice_id = cur.lastrowid
        places_ids_list_of_tuples = [(choice_id, place_id) for place_id in places_ids_list]

        # insert the choices-places records of the new choice to db
        choice_places_query = 'INSERT INTO choices_places (`choice_id`, `place_id`) VALUES (choice_id, %s)'
        cur.executemany(choice_places_query, places_ids_list_of_tuples)

        conn.commit()

    except:
        # if either queries failed - rollback everything
        conn.rollback()

    cur.close()


def update_choice(choice_id):
    if not choice_id:
        raise ValueError('choice_id argument must be not None')

    conn = init_db_connection()
    cur = conn.cursor(mdb.cursors.DictCursor)

    query = 'UPDATE choices SET popularity = popularity + 1 WHERE choice_id = %s'
    try:
        cur.execute(query, (choice_id,))
        conn.commit()
    except:
        conn.rollback()

    cur.close()


def crawl_by_location_shortest_path(center_latitude, center_longitude, page):
    # TODO: delete all usages of this API from js and python
    ADD_HALF_KM_TO_LAT = str(1*10000/111.0)
    ADD_HALF_KM_TO_LONG = str(1*10000/69.0)

    cur = init_db_cursor()

    query = 'Select 	                                                                                            ' \
            '   hotels.id As hid, hotels.google_id As hgid, hotels.name As hn, hotels.rating As hr,                 ' \
            '   hotels.vicinity As hv, hotels.latitude As h_lat, hotels.longitude As h_lon,                         ' \
            '   rid, rgid, rn, rr, rv, r_lat, r_lon,                                                                ' \
            '   bid, bgid, bn, br, bv, b_lat, b_lon,                                                                ' \
            '   muid, mdig, mn, mr, mv,	m_lat, m_lon,                                                               ' \
            '   (sqrt((m_lat - %s)^2 / 100 + (m_lon - %s)^2 / 100) +                                                ' \
            '   sqrt((b_lat - m_lat)^2 / 100 + (b_lon - m_lon)^2 / 100) +                                           ' \
            '   sqrt((r_lat - b_lat)^2 / 100 + (r_lon - b_lon)^2 / 100) +                                           ' \
            '   sqrt((hotels.latitude - r_lat)^2 / 100 + (hotels.longitude - r_lon)^2 / 100))                       ' \
            '   As TotalDistAfterTransp                                                                             ' \
            'From                                                                                                   ' \
            '	places as hotels,                                                                                   ' \
            '	places_categories as pc_hotels,                                                                     ' \
            '	(Select                                                                                             ' \
            '		restaurants.id As rid, restaurants.google_id As rgid, restaurants.name As rn,                   ' \
            '       restaurants.rating As rr, restaurants.vicinity As rv, restaurants.latitude As r_lat,            ' \
            '       restaurants.longitude As r_lon,bid, bgid, bn, br, bv, b_lat, b_lon,                             ' \
            '       muid, mdig, mn, mr, mv,	m_lat, m_lon                                                            ' \
            '		From                                                                                            ' \
            '		places as restaurants,                                                                          ' \
            '		places_categories as pc_restaurants,                                                            ' \
            '		(Select                                                                                         ' \
            '			bars.id As bid, bars.google_id As bgid, bars.name As bn, bars.rating As br,                 ' \
            '           bars.vicinity As bv, bars.latitude As b_lat, bars.longitude As b_lon,                       ' \
            '           muid, mdig, mn, mr, mv,	m_lat, m_lon                                                        ' \
            '		From                                                                                            ' \
            '			places as bars,                                                                             ' \
            '			places_categories as pc_bars,                                                               ' \
            '			(Select                                                                                     ' \
            '				museums.id As muid, museums.google_id As mdig, museums.name as mn,                      ' \
            '               museums.rating as mr, museums.vicinity as mv,museums.latitude As m_lat,                 ' \
            '               museums.longitude As m_lon                                                              ' \
            '				From                                                                                    ' \
            '					places as museums,                                                                  ' \
            '					places_categories as pc_museums	                                                    ' \
            '			    Where                                                                                   ' \
            '					museums.id = pc_museums.place_id                                                    ' \
            '					And pc_museums.category_id = 4                                                      ' \
            '                   And museums.latitude BETWEEN %s - '+ADD_HALF_KM_TO_LAT+'                            ' \
            '                   AND %s + '+ADD_HALF_KM_TO_LAT+'                                                     ' \
            '                   And museums.longitude BETWEEN %s - '+ADD_HALF_KM_TO_LONG+'                          ' \
            '                   AND %s + '+ADD_HALF_KM_TO_LONG+' ) As museums                                       ' \
            '		Where                                                                                           ' \
            '			bars.id = pc_bars.place_id                                                                  ' \
            '			And pc_bars.category_id = 3 And bars.latitude BETWEEN m_lat - '+ADD_HALF_KM_TO_LAT+'        ' \
            '           AND m_lat + '+ADD_HALF_KM_TO_LAT+'                                                          ' \
            '           And bars.longitude BETWEEN m_lon - '+ADD_HALF_KM_TO_LONG+'                                  ' \
            '           AND m_lat + '+ADD_HALF_KM_TO_LONG+' And bars.id <> muid ) As bars                           '\
            '	Where                                                                                               ' \
            '		restaurants.id = pc_restaurants.place_id                                                        ' \
            '		And pc_restaurants.category_id = 2                                                              ' \
            '       And restaurants.latitude BETWEEN b_lat - '+ADD_HALF_KM_TO_LAT+'                                 ' \
            '       AND b_lat + '+ADD_HALF_KM_TO_LAT+'                                                              ' \
            '       AND restaurants.longitude BETWEEN b_lon - '+ADD_HALF_KM_TO_LONG+'                               ' \
            '       AND b_lat + '+ADD_HALF_KM_TO_LONG+'                                                             ' \
            '       And restaurants.id <> bid                                                                       ' \
            '       AND restaurants.id <> muid ) As restaurants                                                     ' \
            'Where                                                                                                  ' \
            '	hotels.id = pc_hotels.place_id                                                                      ' \
            '	And pc_hotels.category_id = 1                                                                       ' \
            '   And hotels.latitude BETWEEN r_lat - '+ADD_HALF_KM_TO_LAT+' AND r_lat + '+ADD_HALF_KM_TO_LAT+'       ' \
            '   AND hotels.longitude BETWEEN r_lon - '+ADD_HALF_KM_TO_LONG+' AND r_lat + '+ADD_HALF_KM_TO_LONG+'    ' \
            '   And hotels.id <> rid                                                                                ' \
            '   And hotels.id <> bid                                                                                ' \
            '   And hotels.id <> muid                                                                               ' \
            'Order By                                                                                               ' \
            '	TotalDistAfterTransp                                                                                ' \
            'Limit                                                                                                  ' \
            '   %s, %s'

    cur.execute(query, (center_longitude, center_longitude, center_latitude,
                        center_latitude, center_longitude, center_longitude,
                        page * DEFAULT_RESULTS_AMOUNT, DEFAULT_RESULTS_AMOUNT))
    rows = cur.fetchall()

    places = dict()
    i = 0
    for result in rows:
        hotel = dict()
        restaurant = dict()
        bar = dict()
        museum = dict()

        hotel["id"] = result["hid"]
        hotel["google_id"] = result["hgid"]
        hotel["name"] = result["hn"]
        hotel["rating"] = result["hr"]
        hotel["vicinity"] = result["hv"]
        hotel["latitude"] = (result["h_lat"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST
        hotel["longitude"] = result["h_lon"] / RESOLUTION

        restaurant["id"] = result["rid"]
        restaurant["google_id"] = result["rgid"]
        restaurant["name"] = result["rn"]
        restaurant["rating"] = result["rr"]
        restaurant["vicinity"] = result["rv"]
        restaurant["latitude"] = (result["r_lat"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST
        restaurant["longitude"] = result["r_lon"] / RESOLUTION

        bar["id"] = result["bid"]
        bar["google_id"] = result["bgid"]
        bar["name"] = result["bn"]
        bar["rating"] = result["br"]
        bar["vicinity"] = result["bv"]
        bar["latitude"] = (result["b_lat"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST
        bar["longitude"] = result["b_lon"] / RESOLUTION

        museum["id"] = result["muid"]
        museum["google_id"] = result["mdig"]
        museum["name"] = result["mn"]
        museum["rating"] = result["mr"]
        museum["vicinity"] = result["mv"]
        museum["latitude"] = (result["m_lat"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST
        museum["longitude"] = result["m_lon"] / RESOLUTION

        places[i] = [hotel, restaurant, bar, museum]
        i += 1

    cur.close()

    return places


# TODO: Yair finish
def crawl_by_location_highest_rating(top, right, bottom, left):
    ADD_HALF_KM_TO_LAT = str(0.5*10000/111.0)
    ADD_HALF_KM_TO_LONG = str(0.5*10000/69.0)

    cur = init_db_cursor()

    # This crawl query returns best rated bar, restaurant and hotels where the hotel is near a given location,
    # and the restaurant near the hotel and the bar is near the restaurant.
    query = 'SELECT hotel_id, hotel_name, hotel_vicinity, hotel_rating, hotel_lat, hotel_long,         '\
            '       rest_id, rest_name, rest_vicinity, rest_rating, rest_lat, rest_long,               '\
            '       p.id AS bar_id, p.name AS bar_name, p.vicinity AS bar_vicinity,                    '\
            '       p.rating AS bar_rating, p.latitude As bar_lat, p.longitude AS bar_long             '\
            'FROM(                                                                                     '\
            '	SELECT best_restaurant.*,MAX(p.rating) as max_rate_of_bar                              '\
            '	FROM(                                                                                  '\
            '		SELECT hotel_id, hotel_name, hotel_vicinity, hotel_rating, hotel_lat, hotel_long,  '\
            '               p.id AS rest_id, p.name AS rest_name, p.vicinity AS rest_vicinity,         '\
            '               p.rating AS rest_rating, p.latitude AS rest_lat, p.longitude AS rest_long  '\
            '		FROM(                                                                              '\
            '                                                                                          '\
            '			SELECT best_hotel.*,MAX(p.rating) as max_rate_of_restaurant                    '\
            '			FROM(                                                                          '\
            '			                                                                               '\
            '				SELECT p.id AS hotel_id, p.name AS hotel_name, p.vicinity as hotel_vicinity,'\
            '                      p.rating AS hotel_rating, p.latitude AS hotel_lat ,p.longitude AS hotel_long'\
            '				FROM places AS p                                                           '\
            '				INNER JOIN                                                                 '\
            '				places_categories AS pc ON p.id = pc.place_id                              '\
            '				WHERE p.latitude BETWEEN %s AND %s                                         '\
            '					  AND p.longitude BETWEEN %s AND %s                                    '\
            '					  AND pc.category_id = 1                                               '\
            '				ORDER BY rating DESC LIMIT 1                                               '\
            '				                                                                           '\
            '				) as best_hotel,                                                           '\
            '			places AS p INNER JOIN                                                         '\
            '			places_categories AS pc ON p.id = pc.place_id                                  '\
            '			WHERE p.latitude BETWEEN hotel_lat - '+ADD_HALF_KM_TO_LAT+'                    '\
            '			AND hotel_lat + '+ADD_HALF_KM_TO_LAT+'                                         '\
            '			AND  p.longitude BETWEEN hotel_long - '+ADD_HALF_KM_TO_LONG+'                  '\
            '			AND hotel_long + '+ADD_HALF_KM_TO_LONG+'                                       '\
            '           AND p.id != hotel_id                                                           '\
            '			AND pc.category_id = 2                                                         '\
            '				                                                                           '\
            '				) AS best_hotel_and_restaurant_rate,                                       '\
            '		places AS p INNER JOIN                                                             '\
            '		places_categories AS pc ON p.id = pc.place_id                                      '\
            '		WHERE p.latitude BETWEEN hotel_lat - '+ADD_HALF_KM_TO_LAT+'                        '\
            '		AND hotel_lat + '+ADD_HALF_KM_TO_LAT+'                                             '\
            '		AND  p.longitude BETWEEN hotel_long - '+ADD_HALF_KM_TO_LONG+'                      '\
            '		AND hotel_long + '+ADD_HALF_KM_TO_LONG+'                                           '\
            '		AND pc.category_id = 2                                                             '\
            '       AND p.id != hotel_id                                                               '\
            '		AND p.rating = max_rate_of_restaurant                                              '\
            '       LIMIT 1                                                                            '\
            '				)AS best_restaurant,                                                       '\
            '	places AS p INNER JOIN                                                                 '\
            '	places_categories AS pc ON p.id = pc.place_id                                          '\
            '	WHERE p.latitude BETWEEN rest_lat - '+ADD_HALF_KM_TO_LAT+'                             '\
            '	AND rest_lat + '+ADD_HALF_KM_TO_LAT+'                                                  '\
            '	AND  p.longitude BETWEEN rest_long - '+ADD_HALF_KM_TO_LONG+'                           '\
            '	AND rest_long + '+ADD_HALF_KM_TO_LONG+'                                                '\
            '   AND p.id != rest_id                                                                    '\
            '	AND pc.category_id = 3                                                                 '\
            '                ) AS best_restaurant_and_bar_rate,                                        '\
            'places AS p INNER JOIN                                                                    '\
            'places_categories AS pc ON p.id = pc.place_id                                             '\
            'WHERE p.latitude BETWEEN rest_lat - '+ADD_HALF_KM_TO_LAT+'                                '\
            'AND rest_lat + '+ADD_HALF_KM_TO_LAT+'                                                     '\
            'AND  p.longitude BETWEEN rest_long - '+ADD_HALF_KM_TO_LONG+'                              '\
            'AND rest_long + '+ADD_HALF_KM_TO_LONG+'                                                   '\
            'AND p.id != rest_id                                                                       '\
            'AND pc.category_id = 3                                                                    '\
            'AND p.rating = max_rate_of_bar                                                            '\
            'LIMIT 1                                                                                   '

    cur.execute(query, (bottom, top, left, right))
    rows = cur.fetchall()


    best_rate_places = {}
    for result in rows:
        best_rate_places[result["hotel_id"]] = {
            "id": result["hotel_id"],
            "name": result["hotel_name"],
            "vicinity": result["hotel_vicinity"],
            "rating": result["hotel_rating"],
            "latitude": (result["hotel_lat"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST,
            "longitude": result["hotel_long"] / RESOLUTION,
            "category": "hotel"
        }

        best_rate_places[result["rest_id"]] = {
            "id": result["rest_id"],
            "name": result["rest_name"],
            "vicinity": result["rest_vicinity"],
            "rating": result["rest_rating"],
            "latitude": (result["rest_lat"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST,
            "longitude": result["rest_long"] / RESOLUTION,
            "category": "restaurant"
        }

        best_rate_places[result["bar_id"]] = {
            "id": result["bar_id"],
            "name": result["bar_name"],
            "vicinity": result["bar_vicinity"],
            "rating": result["bar_rating"],
            "latitude": (result["bar_lat"] / RESOLUTION) + LONDON_LATITUDE_DB_CONST,
            "longitude": result["bar_long"] / RESOLUTION,
            "category": "bar"
        }

    cur.close()

    return best_rate_places
