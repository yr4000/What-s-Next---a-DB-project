from __future__ import division  # is needed to be able to divide like a human being....
import math
from taudb.settings import RESOLUTION, LATITUDE_DIST_DIV_ADJUSTMENT, LONGITUDE_DIST_DIV_ADJUSTMENT,LONDON_LATITUDE_DB_CONST

'''
 for details:
 http://stackoverflow.com/questions/365826/calculate-distance-between-2-gps-coordinates
returns the distance between 2 points in km

 works good comparing to this site:
 http://boulter.com/gps/distance/?from=51.531952%2C+0.003738&to=51.516887%2C+-0.267676&units=k
'''
RESOLUTION = 10000.0
LATITUDE_DIST_DIV_ADJUSTMENT = 111.0  # distance must be in Km!
LONGITUDE_DIST_DIV_ADJUSTMENT = 69.0
LONDON_LATITUDE_DB_CONST = 51


# returns the distance according to two points from type float
def gps_distance(p1, p2):
    r = 6371  # earth's radius in km
    lat1, lat2, lon1, lon2 = p1[0], p2[0], p1[1], p2[1]
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dlat/2)**2 + (math.sin(dlon/2)**2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = r * c  # this is the distance
    return distance
'''
according to:
 http://www.nhc.noaa.gov/gccalc.shtml
for latitude: the second digit from the dot is 1.1 km for each count 1 (up or down)
in longitude: the second digit from the dot is 0.69 km for each count 1 (up or down)
'''


# pre: latitude and longitude ARE NOT modified!
# gets a latitude, longitude (floats) ans d distance, and returns the latitudes and longitudes
# in order to create a square area sizes 2dist*2dist around the point
# TODO: this function is not precise, but maybe for us is good enough. need to check according to map or improve
# TODO: i changed it yet it worked... why?
def get_boundaries_by_center_and_distance(latitude, longitude, dist):
    dist /= 1000  # from meters to km
    top = latitude + dist * RESOLUTION / LATITUDE_DIST_DIV_ADJUSTMENT
    bottom = latitude - dist * RESOLUTION / LATITUDE_DIST_DIV_ADJUSTMENT
    right = longitude + dist * RESOLUTION / LONGITUDE_DIST_DIV_ADJUSTMENT
    left = longitude - dist * RESOLUTION / LONGITUDE_DIST_DIV_ADJUSTMENT
    return int(top), int(right), int(bottom), int(left)


# TODO: itzhaki - refactor this to get 1 point and do the conversion in dataaccess only
def modify_longlat_for_db(latitude, longitude):
    return (latitude-LONDON_LATITUDE_DB_CONST) * RESOLUTION, longitude * RESOLUTION
