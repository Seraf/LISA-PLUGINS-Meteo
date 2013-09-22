from django.conf.urls import patterns, url
from ChatterBot.web import views

urlpatterns = patterns('',
    url(r'^widget$', views.widget1, name='widget'),
)
