from django.test import TestCase
from views import *

# Create your tests here.


# TODO: every point have to be didvided by the resolution in order to use my functions. consider to cancel it
def yair_test(request):
    # return search_places_by_point(51.5363312,-0.0046230,0.5,"places","id, google_id")
    return pub_crawl(51.5363312,-0.0046230)

pub_crawl(51.5363312,-0.0046230)
#search_places_by_point(51.5363312*RESOLUTION,-0.0046230*RESOLUTION,1,"id, google_id","places") #for debug
#search_by_word()
