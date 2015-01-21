"""
Definition of urls for Citypedal.
"""

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

# from bikes.views import home
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Citypedal.views.home', name='home'),
    # url(r'^Citypedal/', include('Citypedal.Citypedal.urls')),
    url(r'^$', 'bikes.views.home', name='home'),
    url(r'^trips/$', 'bikes.views.trips', name='trips'),
    url(r'^trips/(?P<trip_id>\d+)/$', 'bikes.views.trip_details', name='trip-details'),
    url(r'^trips/\+/$', 'bikes.views.trip_new', name='trip-new'),
    url(r'^register/$', 'bikes.views.register', name='register'),
    url(r'^login/$', 'bikes.views.login_view', name='login'),
    url(r'^logout/$', 'bikes.views.logout_view', name='logout'),
    (r'^admin/', include(admin.site.urls)),
)
