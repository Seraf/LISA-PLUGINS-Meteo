from django.conf.urls import patterns, url
from Meteo.web import views

urlpatterns = patterns('',
    url(r'^$',views.index),
)
