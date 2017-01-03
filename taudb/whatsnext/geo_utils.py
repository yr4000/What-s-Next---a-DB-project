from __future__ import division #is needed to be able to divide like a human being....
#import london_coordinates.py
import MySQLdb as mdb
import math

'''
 for details:
 http://stackoverflow.com/questions/365826/calculate-distance-between-2-gps-coordinates
returns the distance between 2 points in km

 works good comparing to this site:
 http://boulter.com/gps/distance/?from=51.531952%2C+0.003738&to=51.516887%2C+-0.267676&units=k
'''

#returns the distance according to two points from type float
def GPSDistance(p1,p2):
    R = 6371 #earth's radious in km
    lat1, lat2, lon1, lon2 = p1[0], p2[0], p1[1], p2[1]
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dlat/2)**2 + (math.sin(dlon/2)**2)*math.cos(lat1)*math.cos(lat2)
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    d = R*c #this is the distance
    return d

'''
according to:
 http://www.nhc.noaa.gov/gccalc.shtml
for latitude: the second digit from the dot is 1.1 km for each count 1 (up or down)
in longitude: the second digit from the dot is 0.69 km for each count 1 (up or down)
'''
#pre: latitude and longitude ARE NOT modified!
#gets a latitude,longtitude (floats) ans d distance, and returns the langtitudes and longtitudes
#in order to create a square area sizes 2dist*2dist arround the point
#TODO this function is not precise, but maybe for us is good enough. need to check according to map or improve
#TODO also, consider modify the function to receive a modified long and lat, and not floats
def getRangeFromKmDistanceAndPoint(latitude,longitude,dist):
    top = latitude+dist/(111)
    right = longitude+dist/(69)
    buttom = latitude-dist/(111)
    left = longitude-dist/(69)
    return top, right, buttom, left

#creates an object used to communicate with the DB
def connectorToDB():
    conn = mdb.connect(host='127.0.0.1', user='DbMysql06', passwd='DbMysql06', db='DbMysql06', port=3305)
    return conn.cursor(mdb.cursors.DictCursor)

#given a query, returns the required rows
def executeQuery(query):
    cur = connectorToDB()
    cur.execute(query)
    return cur.fetchall()