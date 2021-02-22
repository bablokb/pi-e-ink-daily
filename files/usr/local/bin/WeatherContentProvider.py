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
    '201': '6',  # THUNDER RAIN
    '202': '7',  # THUNDER HARD RAIN
    '502': '4',  # HARD RAIN
    '503': '4',  # HARD RAIN
    '504': '4',  # HARD RAIN
    '522': '4',  # HARD RAIN
    '800': '1',  # SUN
    '801': '9',  # SUN AND CLOUD
    '802': '9',  # SUN AND CLOUD
    '803': '9',  # SUN AND CLOUD
    '804': '2'   # CLOUD
    }
  ID_MAP2 = {
    '2': '8',    # THUNDER
    '3': '3',    # RAIN
    '5': '3',    # RAIN
    '6': '5'     # SNOW
    }

  # --- constructor   --------------------------------------------------------
  
  def __init__(self,screen):
    """ constructor """
    super(WeatherContentProvider,self).__init__(screen)

  # --- create fonts   -----------------------------------------------------

  def create_fonts(self):
    """ create fonts """

    self._dseg_font = ImageFont.truetype(self.opts.DSEG_FONT,
                                         self.opts.DSEG_SIZE)
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

  # --- map weather-id to char of DSEG-font   --------------------------------

  def _map_id(self,id):
    """ map weather-id to char of DSEG-font """

    code = str(id)
    # try specific code first
    if code in WeatherContentProvider.ID_MAP1:
      return WeatherContentProvider.ID_MAP1[code]
    # try generic code
    if code[0] in WeatherContentProvider.ID_MAP2:
      return WeatherContentProvider.ID_MAP2[code[0]]
    # otherwise return default ("nothing")
      return ':'

  # --- draw current temperature   -------------------------------------------

  def _draw_current(self,cur,x_off,y_off):
    """ draw current temperature """

    t = "{0:3.1f}°".format(cur.temp)
    t_size = self.canvas.textsize(t,self._big_font,spacing=0)
    x_plus = int((self._size[0]-t_size[0])/2)
    y_plus = int((self._size[1]-t_size[1])/2)
    self.canvas.text((x_off+x_plus,y_off+y_plus),
                     t,font=self._big_font,
                     fill=self.opts.BIG_COLOR)

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
    icon_size = self.canvas.textsize(icon,self._dseg_font,spacing=0)
    x_plus = int((self._size[0]-icon_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+h_size[1]+1+t_size[1]+1),
                     icon,font=self._dseg_font,
                     fill=self.opts.DSEG_COLOR)

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
    icon_size = self.canvas.textsize(icon,self._dseg_font,spacing=0)
    x_plus = int((self._size[0]-icon_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+d_size[1]+1+t_size[1]+1),
                     icon,font=self._dseg_font,
                     fill=self.opts.DSEG_COLOR)
    

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

    if self.screen.rc:
      self.screen.draw_image(self.screen.NO_CONNECT)
      return

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
    h_now = owm.current.dt.hour
    if h_now < 18:
      h_min = max(h_now,8)
      h_max = min(h_min+12,21)
      h_mid = int((h_min+h_max)/2)
    elif h_now < 21:
      h_min = max(h_now,8)
      h_max = min(h_min+12,23)
      h_mid = int((h_min+h_max)/2)
    else:
      h_min = 21
      h_mid = 22
      h_max = 23

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
    for i in range(1,5):
      self._draw_day(owm.days[i],x_off,y_off)
      x_off += self._size[0]
      self.canvas.line([(x_off,y_off),
                              (x_off,y_off+height)],
                             fill=self.opts.LINE_COLOR,width=1)

    self.screen._y_off += height
