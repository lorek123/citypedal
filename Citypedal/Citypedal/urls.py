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
                       url(r'^topup/$', views.topup, name='topup'),
                       url(r'^dispute/(?P<trip_id>\d+)/$', views.dispute,
                           name='dispute'),
                       url(r'^tickets/unresolved/$', views.tickets_admin,
                           name='tickets-admin'),
                       url(r'^tickets/$', views.tickets,
                           name='tickets'),
                       url(r'^ticket/(?P<ticket_id>\d+)/$',
                           views.ticket_details, name='ticket-details'),
                       url(r'^ticket/(?P<ticket_id>\d+)/reject/$',
                           views.ticket_reject, name='ticket-reject'),
                       url(r'^ticket/(?P<ticket_id>\d+)/refund/$',
                           views.ticket_refund, name='ticket-refund'),
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
                       (r'^paypal/', include('paypal.standard.ipn.urls')),
                       )
