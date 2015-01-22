"""
Definition of urls for Citypedal.
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from bikes import views

# from bikes.views import home
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', views.home, name='home'),
                       url(r'^transactions/$', views.transactions,
                           name='transactions'),
                       url(r'^trips/$', views.trips, name='trips'),
                       url(r'^trips/(?P<trip_id>\d+)/finish/$',
                           views.trip_finish, name='trip-finish'),
                       url(r'^trips/(?P<trip_id>\d+)/$',
                           views.trip_details, name='trip-details'),
                       url(r'^trips/\+/$', views.trip_new, name='trip-new'),
                       url(r'^register/$', views.register, name='register'),
                       url(r'^login/$', views.login_view, name='login'),
                       url(r'^logout/$', views.logout_view, name='logout'),
                       (r'^admin/', include(admin.site.urls)),
                       )
