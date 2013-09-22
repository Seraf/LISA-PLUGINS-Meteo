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
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?', params={
            'lang': self.configuration_lisa['lang'],
            'q': ','.join([city,self.configuration_lisa['lang']]),
        })
        print r.url
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
        if "problem" not in weather:
            print weather
            if self.configuration['configuration']['temperature'] == "celsius":
                temptext = _("temp_celsius")
                temp = (((weather['main']['temp'] - 32) * 5) / 9)
            else:
                temptext = _("temp_fahrenheit")
                temp = weather['main']['temp']
            print temptext
            body = ", ".join([
                _('weather in city') % city,
                _('climat') % weather['weather'][0]['description'],
                temptext % str(temp),
                _('humidity') % str(weather['main']['humidity']),
                _('wind speed') % str(weather['wind']['speed'])
            ])
        else:
            body = weather['problem']
        return {"plugin": "ChatterBot",
                "method": "getTime",
                "body": body
        }
