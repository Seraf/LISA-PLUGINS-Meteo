# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup

from lisa.server.plugins.IPlugin import IPlugin
import gettext
import inspect
import os
import requests


class Meteo(IPlugin):
    def __init__(self):
        super(Meteo, self).__init_()
        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "Meteo"})
        self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
            inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
        self._ = translation = gettext.translation(domain='meteo',
                                                   localedir=self.path,
                                                   languages=[self.configuration_lisa['lang']]).ugettext

    def weatherAPI(self, city):
        if self.configuration['configuration']['temperature'] == "celsius":
            units = "metric"
        else:
            units = "imperial"
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?', params={
            'lang': self.configuration_lisa['lang'],
            'units': units,
            'q': ','.join([city, self.configuration_lisa['lang']]),
        })
        if r.ok:
            return r.json()
        else:
            return {"problem": self._('problem contacting server')}

    def getWeather(self, jsonInput):
        if jsonInput['outcome']['entities']['city']['value']:
            city = jsonInput['outcome']['entities']['city']['value']
        else:
            city = self.configuration_plugin['configuration']['city']
        weather = self.weatherAPI(city)
        if self.configuration_plugin['configuration']['temperature'] == "celsius":
            windspeed = round(weather['wind']['speed'] * 3.6)
        else:
            windspeed = round(weather['wind']['speed'] * 2.2369)
        if "problem" not in weather:
            body = ", ".join([
                self._('weather in city') % city,
                self._('climat') % weather['weather'][0]['description'],
                self._("temperature") % round(weather['main']['temp']),
                self._('humidity') % round(weather['main']['humidity']),
                self._('wind speed') % windspeed
            ])
        else:
            body = weather['problem']
        return {"plugin": "Meteo",
                "method": "getWeather",
                "body": body
        }
