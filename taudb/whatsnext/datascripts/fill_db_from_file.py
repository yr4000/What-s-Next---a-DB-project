import csv

import MySQLdb as mdb

'''
                                !!!!! IMPORTANT !!!!!

                             DO NOT RUN THIS FILE!!!!!!
                        EVERYTHING IS IN COMMENT AS A PRECAUTION

                                !!!!! IMPORTANT !!!!!
'''


# def insert_places_to_table():
#     if RUN_LOCAL:
#         conn = mdb.connect(host='127.0.0.1', user='root', passwd='', db='taudb', port=3306, charset='utf8')
#     else:
#         conn = mdb.connect(host='127.0.0.1', user='DbMysql06', passwd='DbMysql06', db='DbMysql06', port=3305,
#                            charset='utf8')
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
#                 try:
#                     cur.executemany(
#                         'INSERT INTO places (`id`,`google_id`,`name`,`rating`,`vicinity`,`latitude`,`longitude`) '
#                         ' VALUES (%s, %s, %s, %s, %s, %s, %s)', tuples_to_add)
#                     i = 1
#                     conn.commit()
#                 except:
#                     conn.rollback()
#                     print 'exception when inserting to places table'
#                     return
#                 print 'inserted {num} tuples to places table'.format(num=len(tuples_to_add))
#                 tuples_to_add = list()
#             i += 1
#
#         # leftovers run for the last tuples that were aggregated
#         try:
#             cur.executemany(
#                 'INSERT INTO places (`id`, `google_id`, `name`, `rating`, `vicinity`, `latitude`, `longitude`) '
#                 ' VALUES (%s, %s, %s, %s, %s, %s, %s)', tuples_to_add)
#             conn.commit()
#             print 'inserted {num} tuples to places table'.format(num=len(tuples_to_add))
#         except:
#             conn.rollback()
#             print 'exception when inserting to places table'
#     cur.close()


# def insert_places_categories_to_table():
#     if RUN_LOCAL:
#         conn = mdb.connect(host='127.0.0.1', user='root', passwd='', db='taudb', port=3306, charset='utf8')
#     else:
#         conn = mdb.connect(host='127.0.0.1', user='DbMysql06', passwd='DbMysql06', db='DbMysql06', port=3305,
#                            charset='utf8')
#     cur = conn.cursor(mdb.cursors.DictCursor)
#
#     with open('places_categories_05_01_17.csv', 'rb') as f:
#         reader = csv.reader(f)
#         i = 1
#         tuples_to_add = list()
#         for id, place_id, category_id in reader:
#             # tuples_to_add.append((id, place_id, category_id)) # This is for places_categories with the id column PK
#             tuples_to_add.append((place_id, category_id))  # This is for places_categories with the double column pk
#
#             if i == 1000:
#                 # insert 1000 tuples at a time
#                 try:
#                     # This is for places_categories with the id column PK
#                     # cur.executemany(
#                     #     'INSERT INTO places_categories (`id`, `place_id`, `category_id`) '
#                     #     ' VALUES (%s, %s, %s)', tuples_to_add)
#
#                     # This is for places_categories with the double column pk
#                     cur.executemany(
#                         'INSERT INTO places_categories_v3 (`place_id`, `category_id`) '
#                         ' VALUES (%s, %s)', tuples_to_add)
#                     i = 1
#                     conn.commit()
#                 except:
#                     conn.rollback()
#                     print 'exception when inserting to places_categories table'
#                     return
#                 print 'inserted {num} tuples to places_categories table'.format(num=len(tuples_to_add))
#                 tuples_to_add = list()
#             i += 1
#
#         # leftovers run for the last tuples that were aggregated
#         try:
#             # This is for places_categories with the id column PK
#             # cur.executemany(
#             #     'INSERT INTO places_categories (`id`, `place_id`, `category_id`) '
#             #     ' VALUES (%s, %s, %s)', tuples_to_add)
#
#             # This is for places_categories with the double column pk
#             cur.executemany(
#                 'INSERT INTO places_categories_v3 (`place_id`, `category_id`) '
#                 ' VALUES (%s, %s)', tuples_to_add)
#             conn.commit()
#             print 'inserted {num} tuples to places_categories table'.format(num=len(tuples_to_add))
#         except:
#             conn.rollback()
#             print 'exception when inserting to places_categories table'
#     cur.close()

# RUN_LOCAL = False
# insert_places_to_table()
# insert_places_categories_to_table()
