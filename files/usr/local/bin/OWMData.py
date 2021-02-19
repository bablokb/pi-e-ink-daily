#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# Interface to OpenWeatherMap One-Call API. Used by WeatherContentProvider.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

import requests, json, datetime

# --- helper class (value-holder)   ------------------------------------------

class Values(object):
  pass

# --- interface to OWM-one-call API (subset)   -------------------------------

class OWMData(object):
  # API-URL from OpenWeatherMap
  URL = "https://api.openweathermap.org/data/2.5/onecall?lat={0}&lon={1}&exclude=minutely,alerts&appid={2}&units=metric"

  # wind-direction constants
  DIRECTION = ['N','NE','E','SE','S','SW','W','NW','N']
  
  def __init__(self,latitude,longitude,api_key):
    self._latitude  = latitude
    self._longitude = longitude
    self._api_key   = api_key

    self.current = None
    self.hours   = []
    self.days    = []

  # --- parse data   ---------------------------------------------------------

  def _parse_data(self,wdict):
    """ parse data from weather-dict """
 
    val            = Values()
    val.dt         = datetime.datetime.fromtimestamp(wdict["dt"])
    if isinstance(wdict["temp"],(int,float)):
      val.temp       = wdict["temp"]
      val.tmin       = wdict["temp"]
      val.tmax       = wdict["temp"]
    else:
      val.temp       = wdict["temp"]["day"]
      val.tmin       = wdict["temp"]["min"]
      val.tmax       = wdict["temp"]["max"]
    val.pressure   = wdict["pressure"]
    val.humidity   = wdict["humidity"]
    val.wind_speed = wdict["wind_speed"]
    val.wind_deg   = wdict["wind_deg"]
    val.wind_dir   = OWMData.DIRECTION[int((int(val.wind_deg)+22.5)/45)]
    val.id         = wdict["weather"][0]["id"]
    val.icon       = wdict["weather"][0]["icon"]
    return val

  # --- query weather-data from OWM   ----------------------------------------

  def update(self):
    """ query weather data """

    url = OWMData.URL.format(self._latitude,self._longitude,self._api_key)

    # query data
    response = requests.get(url)
    data = json.loads(response.text)
    response.close()

    # current
    self.current = self._parse_data(data["current"])
    
    # next hour forecast
    self.hours.clear()
    for hour in data["hourly"]:
      self.hours.append(self._parse_data(hour))

    # next days forecast
    self.days.clear()
    for day in data["daily"]:
      self.days.append(self._parse_data(day))

  # --- print value-object   -------------------------------------------------

  def print(self,label,wo):
    """ print value-object """

    print("---------------- %s ---------------" % label)
    print("Date:     %s" % wo.dt.strftime("%d.%m.%Y %H:%M:%S"))
    print("Temp:     %r °C" % wo.temp)
    print("Min:      %r °C" % wo.tmin)
    print("Max:      %r °C" % wo.tmax)
    print("Pressure: %r hPa" % wo.pressure)
    print("Humidity: %r%%" % wo.humidity)
    print("W-speed:  %r m/s" % wo.wind_speed)
    print("W-deg:    %r°" % wo.wind_deg)
    print("W-dir:    %s" % wo.wind_dir)
    print("")

  # --- print complete object   ----------------------------------------------

  def print_all(self):
    """ print complete object """

    self.print("Current",self.current)
    for hour in self.hours:
      self.print("Hour",hour)
    for day in self.days:
      self.print("Day",day)
