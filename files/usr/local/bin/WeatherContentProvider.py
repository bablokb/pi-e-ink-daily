#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# Content-provider for the weather forecast from OpenWeatherMap
#
# This class draws two lines of tiles:
#   - the first line has three tiles for the current day
#   - the second line has four tiles for the next four days
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

import requests, traceback

from ContentProvider import ContentProvider
from OWMData         import OWMData

class WeatherContentProvider(ContentProvider):

  # --- constructor   --------------------------------------------------------
  
  def __init__(self,screen):
    """ constructor """
    super(WeatherContentProvider,self).__init__(screen)

  # --- calculate available space for tiles   --------------------------------

  def _calc_tile_sizes(self):
    """ calculate tile sizes """

    # screen-height - current offset - height of status-line
    height = int((self.opts.HEIGHT - self.screen._y_off -
                                            self.opts.HEIGHT_S)/2)
    width3 = int(self.opts.WIDTH/3)
    width4 = int(self.opts.WIDTH/4)
    self._sizes = ((width3,height),(width4,height))

  # --- draw hourly forecast   -----------------------------------------------

  def _draw_hour(self,hour,x_off,y_off):
    """ draw forecast for given hour """

    # hour
    h = hour.dt.strftime("%H:%M")
    h_size = self.canvas.textsize(h,self.screen._text_font,spacing=0)
    x_plus = int((self._sizes[0][0]-h_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off),
                     h,font=self.screen._text_font,
                      fill=self.opts.TEXT_COLOR)
    # temp
    t = "{0:3.1f}°".format(hour.temp)
    t_size = self.canvas.textsize(t,self.screen._text_font,spacing=0)
    x_plus = int((self._sizes[0][0]-t_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+t_size[1]+1),
                     t,font=self.screen._text_font,
                     fill=self.opts.TEXT_COLOR)
    
  # --- draw daily forecast   ------------------------------------------------

  def _draw_day(self,day,x_off,y_off):
    """ draw forecast for given day """

    # day
    d = day.dt.strftime("%a %d.%m.")
    d_size = self.canvas.textsize(d,self.screen._text_font,spacing=0)
    x_plus = int((self._sizes[1][0]-d_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off),
                     d,font=self.screen._text_font,
                      fill=self.opts.TEXT_COLOR)
    # temp
    t = "{0:d}°/{1:d}°".format(round(day.tmin),round(day.tmax))
    t_size = self.canvas.textsize(t,self.screen._text_font,spacing=0)
    x_plus = int((self._sizes[1][0]-t_size[0])/2)
    self.canvas.text((x_off+x_plus,y_off+t_size[1]+1),
                     t,font=self.screen._text_font,
                     fill=self.opts.TEXT_COLOR)
    

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

    # hourly forecast
    x_off  = 0
    y_off  = self.screen._y_off
    height = self._sizes[0][1]
    for i in range(1,4):
      self._draw_hour(owm.hours[i],x_off,y_off)
      x_off += self._sizes[0][0]
      self.canvas.line([(x_off,y_off),
                                (x_off,y_off+height)],
                               fill=self.opts.LINE_COLOR,width=1)

    self.screen._y_off += height
    self.screen._draw_hline(self.screen._y_off)

    # daily forecast
    x_off = 0
    y_off  = self.screen._y_off
    height = self._sizes[1][1]
    for i in range(1,5):
      self._draw_day(owm.days[i],x_off,y_off)
      x_off += self._sizes[1][0]
      self.canvas.line([(x_off,y_off),
                              (x_off,y_off+height)],
                             fill=self.opts.LINE_COLOR,width=1)

    self.screen._y_off += height
