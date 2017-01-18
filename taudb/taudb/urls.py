"""taudb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from whatsnext import views, tests

urlpatterns = [
    url(r'^admin/', admin.site.urls),
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
