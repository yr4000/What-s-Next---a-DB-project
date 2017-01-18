from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.homepage),
    url(r'^searchByFullText', views.search_by_name),
    url(r'^searchCombinationByPoint', views.find_suggestion_by_point),
    url(r'^place/(?P<place_id>\d+)/details', views.get_place_details),
    url(r'^place/get_around_marker/', views.search_places_by_point),
    url(r'^stats/categories', views.calc_categories_statistics),
    url(r'^stats/top_places', views.calc_top_places_for_category),
    url(r'^stats/top_choices', views.calc_top_choices),
    url(r'^updatePopularSearches', views.update_popular_search),
    url(r'^ImFeelingLucky', views.im_feeling_lucky)
    ]
