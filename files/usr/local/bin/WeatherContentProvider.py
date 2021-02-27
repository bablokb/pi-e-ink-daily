#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# Content-provider for the weather forecast from OpenWeatherMap
#
# This class draws two lines of tiles:
#   - the first line has four tiles for the current day (now and three hours)
#   - the second line has four tiles for the next four days
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

import requests, traceback

from PIL import ImageFont

from ContentProvider import ContentProvider
from OWMData         import OWMData

class WeatherContentProvider(ContentProvider):

  ID_MAP1 = {
    200: "\uf01e",   #thunderstorm
    201: "\uf01e",   #thunderstorm
    202: "\uf01e",   #thunderstorm
    210: "\uf016",   #lightning
    211: "\uf016",   #lightning
    212: "\uf016",   #lightning
    221: "\uf016",   #lightning
    230: "\uf01e",   #thunderstorm
    231: "\uf01e",   #thunderstorm
    232: "\uf01e",   #thunderstorm
    300: "\uf01c",   #sprinkle
    301: "\uf01c",   #sprinkle
    302: "\uf019",   #rain
    310: "\uf017",   #rain-mix
    311: "\uf019",   #rain
    312: "\uf019",   #rain
    313: "\uf01a",   #showers
    314: "\uf019",   #rain
    321: "\uf01c",   #sprinkle
    500: "\uf019",   #light rain
    501: "\uf019",   #moderate rain
    502: "\uf015",   #heavy intense rain
    503: "\uf018",   #very heavy rain
    504: "\uf018",   #extreme rain
    511: "\uf017",   #freezing rain
    520: "\uf01c",   #light intensity showers
    521: "\uf01a",   #rain showers
    522: "\uf015",   #heavy rain showers
    531: "\uf01d",   #storm-showers
    600: "\uf01b",   #light snow
    601: "\uf01b",   #snow
    602: "\uf064",   #heavy snow
    611: "\uf0b5",   #sleet
    612: "\uf017",   #light shower sleet
    612: "\uf017",   #shower sleet
    615: "\uf017",   #light rain and snow
    616: "\uf017",   #rain and snow
    620: "\uf01b",   #light shower snow
    621: "\uf01b",   #shower snow
    622: "\uf064",   #heavy shower snow
    701: "\uf014",   #mist
    711: "\uf062",   #smoke
    721: "\uf063",   #haze
    731: "\uf063",   #dust
    741: "\uf021",   #fog
    751: "\uf063",   #sand
    761: "\uf063",   #dust
    762: "\uf063",   #dust
    771: "\uf014",   #squalls
    781: "\uf056",   #tornado
    800: "\uf00d",   #sunny
    801: "\uf041",   #cloud
    802: "\uf00c",   #clouds  25-50%
    803: "\uf002",   #clouds  51-84%
    804: "\uf013",   #clouds  85-100%
    900: "\uf056",   #tornado
    901: "\uf01d",   #storm-showers
    902: "\uf073",   #hurricane
    903: "\uf076",   #snowflake-cold
    904: "\uf055",   #hot
    905: "\uf021",   #windy
    906: "\uf015",   #hail
    957: "\uf050"    #strong-wind
    }
  ID_MAP2 = {
    '2': "\uf01e",   #thunderstorm
    '3': "\uf019",   #rain
    '5': "\uf019",   #rain
    '6': "\uf01b"    #snow
    }
  DIR_MAP = {
    "N":  "\uF060",
    "NE": "\uF05E",
    "E":  "\uF061",
    "SE": "\uF05B",
    "S":  "\uF05C",
    "SW": "\uF05A",
    "W":  "\uF059",
    "NW": "\uF05D"
    }

  # --- constructor   --------------------------------------------------------
  
  def __init__(self,screen):
    """ constructor """
    super(WeatherContentProvider,self).__init__(screen)

  # --- create fonts   -----------------------------------------------------

  def create_fonts(self):
    """ create fonts """

    # weather-icons
    self._wi_font = ImageFont.truetype(self.opts.WI_FONT,
                                         self.opts.WI_SIZE)
    # wind-direction icons
    self._wdir_font = ImageFont.truetype(self.opts.WDIR_FONT,
                                         self.opts.WDIR_SIZE)
    self._big_font  = ImageFont.truetype(self.opts.BIG_FONT,
                                         self.opts.BIG_SIZE)

  # --- calculate available space for tiles   --------------------------------

  def _calc_tile_sizes(self):
    """ calculate tile sizes """

    # screen-height - current offset - height of status-line
    height = int((self.opts.HEIGHT - self.screen._y_off -
                                            self.opts.HEIGHT_S)/2)
    width4 = int(self.opts.WIDTH/4)
    self._size = ((width4,height))

  # --- map weather-id to char of WI-font   --------------------------------

  def _map_id(self,id):
    """ map weather-id to char of WI-font """

    # try specific code first
    if id in WeatherContentProvider.ID_MAP1:
      return WeatherContentProvider.ID_MAP1[id]
    # try generic code
    code = str(id)[0]
    if code in WeatherContentProvider.ID_MAP2:
      return WeatherContentProvider.ID_MAP2[code]
    # otherwise return default ("n/a")
      return "\uf07b"

  # --- draw current temperature   -------------------------------------------

  def _draw_current(self,cur,x_off,y_off):
    """ draw current temperature """

    # current temperature
    t = "{0:3.1f}°".format(cur.temp)
    t_size = self.canvas.textsize(t,self._big_font,spacing=0)
    x_plus = int((self._size[0]-t_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off),
                     t,font=self._big_font,
                     fill=self.opts.BIG_COLOR)

    # wind direction icon
    icon = self.DIR_MAP[cur.wind_dir]
    icon_size = self.canvas.textsize(icon,self._wdir_font,spacing=0)
    x_plus = int((self._size[0]-icon_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+t_size[1]+1),
                     icon,font=self._wdir_font,
                     fill=self.opts.WDIR_COLOR)

    # wind speed
    s = "{0:d} km/h".format(round(cur.wind_speed))
    s_size = self.canvas.textsize(s,self.screen._text_font,spacing=0)
    x_plus = int((self._size[0]-s_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+t_size[1]+1+icon_size[1]+2),
                     s,font=self.screen._text_font,
                     fill=self.opts.TEXT_COLOR)

  # --- draw hourly forecast   -----------------------------------------------

  def _draw_hour(self,hour,x_off,y_off):
    """ draw forecast for given hour """

    # hour
    h = hour.dt.strftime("%H:%M")
    h_size = self.canvas.textsize(h,self.screen._text_font,spacing=0)
    x_plus = int((self._size[0]-h_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off),
                     h,font=self.screen._text_font,
                      fill=self.opts.TEXT_COLOR)
    # temp
    t = "{0:3.1f}°".format(hour.temp)
    t_size = self.canvas.textsize(t,self.screen._text_font,spacing=0)
    x_plus = int((self._size[0]-t_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+h_size[1]+1),
                     t,font=self.screen._text_font,
                     fill=self.opts.TEXT_COLOR)
    # icon
    icon = self._map_id(hour.id)
    icon_size = self.canvas.textsize(icon,self._wi_font,spacing=0)
    x_plus = int((self._size[0]-icon_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+h_size[1]+1+t_size[1]+1),
                     icon,font=self._wi_font,
                     fill=self.opts.WI_COLOR)

  # --- draw daily forecast   ------------------------------------------------

  def _draw_day(self,day,x_off,y_off):
    """ draw forecast for given day """

    # day
    d = day.dt.strftime("%a %d.%m.")
    d_size = self.canvas.textsize(d,self.screen._text_font,spacing=0)
    x_plus = int((self._size[0]-d_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off),
                     d,font=self.screen._text_font,
                      fill=self.opts.TEXT_COLOR)
    # temp
    t = "{0:d}°/{1:d}°".format(round(day.tmin),round(day.tmax))
    t_size = self.canvas.textsize(t,self.screen._text_font,spacing=0)
    x_plus = int((self._size[0]-t_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+d_size[1]+1),
                     t,font=self.screen._text_font,
                     fill=self.opts.TEXT_COLOR)
    # icon
    icon = self._map_id(day.id)
    icon_size = self.canvas.textsize(icon,self._wi_font,spacing=0)
    x_plus = int((self._size[0]-icon_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+d_size[1]+1+t_size[1]+1),
                     icon,font=self._wi_font,
                     fill=self.opts.WI_COLOR)
    

  # --- draw content on screen   ---------------------------------------------

  def draw_content(self):
    """ draw weather-info """

    try:
      owm = OWMData(self.opts.owm_latitude,
                    self.opts.owm_longitude,
                    self.opts.owm_apikey)
      owm.update()
    except:
      traceback.print_exc()
      self.screen.rc = 3
      return                             # ignore error, don't update display

    self._calc_tile_sizes()

    # current temperature
    height = self._size[1]
    x_off = 0
    y_off = self.screen._y_off
    self._draw_current(owm.current,x_off,y_off)
    x_off += self._size[0]
    self.canvas.line([(x_off,y_off),
                      (x_off,y_off+height)],
                               fill=self.opts.LINE_COLOR,width=1)

    # hourly forecast: three hours between 08:00 and 21:00
    h_now   = owm.current.dt.hour
    day_off = 1
    if h_now < 18:
      h_min = max(h_now+1,8)
      h_max = min(h_min+12,21)
      h_mid = int((h_min+h_max)/2)
    elif h_now < 21:
      h_min = h_now+1
      h_max = 23
      h_mid = int((h_min+h_max)/2)
    else:
      h_min   = 32   # 08:00 next day
      h_mid   = 38   # 14:00 next day
      h_max   = 44   # 20:00 next day
      day_off = 2    # increase day-offset

    for i in [h_min-h_now,h_mid-h_now,h_max-h_now]:
      self._draw_hour(owm.hours[i],x_off,y_off)
      x_off += self._size[0]
      self.canvas.line([(x_off,y_off),
                                (x_off,y_off+height)],
                               fill=self.opts.LINE_COLOR,width=1)

    self.screen._y_off += height
    self.screen._draw_hline(self.screen._y_off)

    # daily forecast
    x_off = 0
    y_off  = self.screen._y_off
    height = self._size[1]
    for i in range(day_off,4+day_off):
      self._draw_day(owm.days[i],x_off,y_off)
      x_off += self._size[0]
      self.canvas.line([(x_off,y_off),
                              (x_off,y_off+height)],
                             fill=self.opts.LINE_COLOR,width=1)

    self.screen._y_off += height
