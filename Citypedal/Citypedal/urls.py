"""
Definition of urls for Citypedal.
"""

from django.conf.urls import patterns, include, url
from django.conf import settings

# from bikes.views import home
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Citypedal.views.home', name='home'),
    # url(r'^Citypedal/', include('Citypedal.Citypedal.urls')),
    url(r'^$', 'bikes.views.home', name='home'),
    
)
