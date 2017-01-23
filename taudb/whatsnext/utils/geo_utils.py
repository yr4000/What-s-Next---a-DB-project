from __future__ import division  # is needed to be able to divide like a human being....
import math

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

# pre: latitude and longitude ARE NOT modified!
# gets a latitude, longitude (floats) ans d distance, and returns the latitudes and longitudes
# in order to create a square area sizes 2dist*2dist around the point
def get_boundaries_by_center_and_distance(latitude, longitude, dist):
    dist /= 1000  # from meters to km
    top = latitude + dist * RESOLUTION / LATITUDE_DIST_DIV_ADJUSTMENT
    bottom = latitude - dist * RESOLUTION / LATITUDE_DIST_DIV_ADJUSTMENT
    right = longitude + dist * RESOLUTION / LONGITUDE_DIST_DIV_ADJUSTMENT
    left = longitude - dist * RESOLUTION / LONGITUDE_DIST_DIV_ADJUSTMENT
    return int(top), int(right), int(bottom), int(left)


def modify_longlat_for_db(latitude, longitude):
    return (latitude - LONDON_LATITUDE_DB_CONST) * RESOLUTION, longitude * RESOLUTION
