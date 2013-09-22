# -*- coding: UTF-8 -*-
import json, os, inspect
from pymongo import MongoClient
from lisa import configuration
import requests

import gettext

path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
    inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
_ = translation = gettext.translation(domain='meteo', localedir=path, languages=[configuration['lang']]).ugettext

class Meteo:
    def __init__(self, lisa=None):
        if lisa is not None:
            self.lisa = lisa
        self.configuration_lisa = configuration
        self.mongo = MongoClient(host=self.configuration_lisa['database']['server'],
                            port=self.configuration_lisa['database']['port'])
        self.configuration = self.mongo.lisa.plugins.find_one({"name": "Meteo"})

    def weatherAPI(self, city):
        if self.configuration['configuration']['temperature'] == "celsius":
            units = "metric"
        else:
            units = "imperial"
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?', params={
            'lang': self.configuration_lisa['lang'],
            'units': units,
            'q': ','.join([city,self.configuration_lisa['lang']]),
        })
        if r.ok:
            return r.json()
        else:
            return {"problem": _('problem contacting server')}

    def getWeather(self, jsonInput):
        if jsonInput['outcome']['entities']['city']['value']:
            city = jsonInput['outcome']['entities']['city']['value']
        else:
            city = self.configuration['configuration']['city']
        weather = self.weatherAPI(city)
        if self.configuration['configuration']['temperature'] == "celsius":
            windspeed = round(weather['wind']['speed'] * 3.6)
        else:
            windspeed = round(weather['wind']['speed'] * 2.2369)
        if "problem" not in weather:
            body = ", ".join([
                _('weather in city') % city,
                _('climat') % weather['weather'][0]['description'],
                _("temperature") % round(weather['main']['temp']),
                _('humidity') % round(weather['main']['humidity']),
                _('wind speed') % windspeed
            ])
        else:
            body = weather['problem']
        return {"plugin": "ChatterBot",
                "method": "getTime",
                "body": body
        }
