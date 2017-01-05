from django.conf import settings
import MySQLdb


# Creates an connection  with the DB
def init_db_connection():
    return MySQLdb.connect(host=settings.DB_HOST, user=settings.DB_ALL, passwd=settings.DB_ALL,
                           db=settings.DB_ALL, port=settings.DB_PORT)


# Creates an object used to send queries to the DB
def init_db_cursor():
    conn = init_db_connection()
    return conn.cursor(MySQLdb.cursors.DictCursor)


# Given a query, returns the required rows
def execute_query(query):
    cursor = init_db_cursor()
    cursor.execute(query)
    return cursor.fetchall()
