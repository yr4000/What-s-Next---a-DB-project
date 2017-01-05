from ..geo_utils import connectorToDB
from whatsnext.models import Review, Place
from exceptions import NotFoundInDb
import MySQLdb as mdb


def get_place_by_place_id(place_id):
    if not place_id:
        raise ValueError('id argument must be not None')

    cur = connectorToDB()

    query = 'SELECT' \
            '   places.id AS place_id, ' \
            '   places.google_id, ' \
            '   places.name, ' \
            '   places.rating, ' \
            '   places.vicinity, ' \
            '   places.latitude, ' \
            '   places.longitude, ' \
            '   categories.name AS category ' \
            'FROM' \
            '   places ' \
            '       INNER JOIN ' \
            '   places_categories ON places.id = places_categories.place_id ' \
            '       INNER JOIN ' \
            '   categories ON places_categories.category_id = categories.id ' \
            'WHERE' \
            '   places.id = {place_id}'.format(place_id=place_id)

    cur.execute(query)

    record = cur.fetchone()  # expecting single place since id is a pk
    if record:
        place = Place(**record)
    else:
        raise NotFoundInDb('db does not include a record with id: {id}'.format(id=id))

    cur.close()

    return place


def get_place_reviews(place):
    if not place:
        raise ValueError('place argument must be not None')

    cur = connectorToDB()

    query = 'SELECT' \
            '   reviews.id as review_id, ' \
            '   reviews.place_id, ' \
            '   reviews.author, ' \
            '   reviews.rating, ' \
            '   reviews.text, ' \
            '   reviews.date ' \
            'FROM' \
            '   reviews ' \
            'WHERE' \
            '   reviews.place_id = {place_id}'.format(place_id=place.place_id)

    cur.execute(query)

    records = cur.fetchall()

    reviews = list()
    for record in records:
        review = Review(**record)
        reviews.append(review)

    cur.close()

    return reviews


def insert_review_to_db(review):
    if not review:
        raise ValueError('id argument must be not None')

    # TODO: should use an object to obtain the connection and cursor
    conn = mdb.connect(host='127.0.0.1', user='DbMysql06', passwd='DbMysql06', db='DbMysql06', port=11211)
    cur = conn.cursor(mdb.cursors.DictCursor)

    # TODO: check what happens if review.date is None
    cur.execute('INSERT INTO reviews (`place_id`, `author`, `rating`, `text`, `date`) '
                'VALUES (%s, %s, %s, %s, %s)',
                (review.place_id, review.author, review.rating, review.text, review.date))

    conn.commit()

    review.review_id = cur.lastrowid
    cur.close()

