import csv

import MySQLdb as mdb

'''
                                !!!!! IMPORTANT !!!!!

                DO NOT RUN THIS FILE UNLESS YOUR NAME IS ALON ITZHAKI!!!!!!
                        EVERYTHING IS IN COMMENT AS A PRECAUTION

                                (is my name Alon Itzhaki?)

                                !!!!! IMPORTANT !!!!!
'''


# def insert_places_to_table():
#     conn = mdb.connect(host='127.0.0.1', user='DbMysql06', passwd='DbMysql06', db='DbMysql06', port=3305,
#                        charset='utf8')
#     cur = conn.cursor(mdb.cursors.DictCursor)
#
#     with open('places_05_01_17_converted.csv', 'rb') as f:
#         reader = csv.reader(f)
#         i = 1
#         tuples_to_add = list()
#         for id, google_id, name, rating, vicinity, latitude, longitude in reader:
#             tuples_to_add.append((id, google_id, name, rating, vicinity, latitude, longitude))
#
#             if i == 1000:
#                 # insert 1000 tuples at a time
#                 cur.executemany(
#                     'INSERT INTO places (`id`, `google_id`, `name`, `rating`, `vicinity`, `latitude`, `longitude`) '
#                     ' VALUES (%s, %s, %s, %s, %s, %s, %s)', tuples_to_add)
#                 i = 1
#                 conn.commit()
#                 print 'inserted {num} tuples to places table'.format(num=len(tuples_to_add))
#                 tuples_to_add = list()
#             i += 1
#
#         # leftovers run for the last tuples that were aggregated
#         cur.executemany(
#             'INSERT INTO places (`id`, `google_id`, `name`, `rating`, `vicinity`, `latitude`, `longitude`) '
#             ' VALUES (%s, %s, %s, %s, %s, %s, %s)', tuples_to_add)
#         conn.commit()
#         print 'inserted {num} tuples to places table'.format(num=len(tuples_to_add))
#     cur.close()


# def insert_places_categories_to_table():
#     conn = mdb.connect(host='127.0.0.1', user='DbMysql06', passwd='DbMysql06', db='DbMysql06', port=3305,
#                        charset='utf8')
#     cur = conn.cursor(mdb.cursors.DictCursor)
#
#     with open('places_categories_05_01_17.csv', 'rb') as f:
#         reader = csv.reader(f)
#         i = 1
#         tuples_to_add = list()
#         for id, place_id, category_id in reader:
#             tuples_to_add.append((id, place_id, category_id))
#
#             if i == 1000:
#                 # insert 1000 tuples at a time
#                 cur.executemany(
#                     'INSERT INTO places_categories (`id`, `place_id`, `category_id`) '
#                     ' VALUES (%s, %s, %s)', tuples_to_add)
#                 i = 1
#                 conn.commit()
#                 print 'inserted {num} tuples to places_categories table'.format(num=len(tuples_to_add))
#                 tuples_to_add = list()
#             i += 1
#
#         # leftovers run for the last tuples that were aggregated
#         cur.executemany(
#             'INSERT INTO places_categories (`id`, `place_id`, `category_id`) '
#             ' VALUES (%s, %s, %s)', tuples_to_add)
#         conn.commit()
#         print 'inserted {num} tuples to places_categories table'.format(num=len(tuples_to_add))
#     cur.close()


# insert_places_to_table()
# insert_places_categories_to_table()
