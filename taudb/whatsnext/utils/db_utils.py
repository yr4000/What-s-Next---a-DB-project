from django.conf import settings
import MySQLdb


# Creates an connection  with the DB
def init_db_connection():
    return MySQLdb.connect(host=settings.DB_HOST, user=settings.DB_ALL, passwd=settings.DB_ALL,
                           db=settings.DB_ALL, port=settings.DB_PORT, charset=settings.DB_CHARSET)


# Creates an object used to send queries to the DB
def init_db_cursor():
    conn = init_db_connection()
    return conn.cursor(MySQLdb.cursors.DictCursor)


# Given a query, returns the required rows
def execute_sfw_query(query):
    cursor = init_db_cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows


# Given an UPDATE or INSERT query, commits it.
def execute_writing_query(query):
    dbb = init_db_connection()
    cursor = dbb.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query)
    dbb.commit()
    cursor.close()
    dbb.close()


# returns a query string of a view according to relevant parameters
def create_view_from_parameters(tables_list, columns_list="*"):
    query = "SELECT"
    for i in range(len(columns_list)):
        query += " " + columns_list[i] + ", "
    query += " FROM"
    for i in range(len(tables_list)):
        query += " " + tables_list[i] + ", "
    return query
