#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# The code is configurable for any display - you must only update the
# display output.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

CONFIG_FILE_DEFAULT = "/etc/pi-e-ink-daily.defaults.json"
CONFIG_FILE         = "/etc/pi-e-ink-daily.json"

import traceback

# --- system-imports   -------------------------------------------------------

import argparse
import sys, os, datetime, locale, json

from PIL import Image, ImageDraw, ImageFont

try:
  from inky.auto import auto
  inky_available = True
except Exception:
  # traceback.print_exc()
  inky_available = False

# ----------------------------------------------------------------------------
# --- helper class to convert a dict to an object   --------------------------

class Options(object):
  def __init__(self,d):
    self.__dict__ = d

# ----------------------------------------------------------------------------
# --- main application class   -----------------------------------------------

class DailyAgenda(object):
  """ main application class """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    global inky_available
    if inky_available:
      try:
        self._display = auto()
        if self._display.colour != "multi":
          self._display.GRAY   = self._display.RED
          self._display.GREEN  = self._display.RED
          self._display.BLUE   = self._display.RED
          self._display.ORANGE = self._display.RED
        else:
          self._display.GRAY   = self._display.RED
      except Exception:
        inky_available = False    # only the lib is available

    if not inky_available:
      self._display = Options( {
        'WHITE' : (255,255,255),
        'BLACK' : (0,0,0),
        'GRAY'  : (192,192,192),
        'RED'   : (255,0,0),
        'YELLOW': (255,255,0),
        'GREEN' : (0,128,0),
        'BLUE'  : (0,0,255),
        'ORANGE': (255,165,0)
        })

    # read settings. This has to be done twice: the first
    # time to query the content-provider, the second time
    # to overwrite default settings of content-provider
    self._opts = {}
    self._read_settings()
    self._get_content_provider()
    self.provider.read_settings()
    self._read_settings()
    self._opts = Options(self._opts)     # convert to attributes

    # drawing objects
    self._create_color_maps()            # create color-maps
    self._map_colors()
    self._create_fonts()

    # path to images
    pgm_dir = os.path.dirname(os.path.realpath(__file__))
    img_dir = os.path.realpath(os.path.join(pgm_dir,"..",
                                            "share","pi-e-ink-daily"))
    self.NO_CONNECT = os.path.join(img_dir,self._opts.no_server_connection)
    self.NO_EVENTS  = os.path.join(img_dir,self._opts.no_events)


    # application objects
    if inky_available:
      self._opts.WIDTH=self._display.width
      self._opts.HEIGHT=self._display.height

      self._image  = Image.new("P",
                             (self._opts.WIDTH,self._opts.HEIGHT),
                             color=self._opts.BORDER_COLOR)
    else:
      self._image  = Image.new("RGB",
                             (self._opts.WIDTH,self._opts.HEIGHT),
                             color=self._opts.BORDER_COLOR)

    self._canvas = ImageDraw.Draw(self._image)
    self.provider.set_canvas(self._canvas)
    self._y_off  = 0
    self.rc = 0                   # return-code

  # --- load content provider   ----------------------------------------------

  def _get_content_provider(self):
    """ load content provider """

    mod = __import__(self._opts["content_provider"])
    klass = getattr(mod,self._opts["content_provider"])
    self.provider = klass(self)

  # --- create color-maps   --------------------------------------------------

  def _create_color_maps(self):
    """ create color-maps """

    self._cmap = {
      'white' : self._display.WHITE,
      'black' : self._display.BLACK,
      'gray'  : self._display.RED,
      'red'   : self._display.RED,
      'yellow': self._display.YELLOW,
      'green' : self._display.GREEN,
      'blue'  : self._display.BLUE,
      'orange': self._display.ORANGE
      }

    # map bg-color to suitable fg-color
    self._bg_map = {
      self._display.WHITE:  self._display.BLACK,
      self._display.BLACK:  self._display.WHITE,
      self._display.GRAY:   self._display.BLACK,
      self._display.RED:    self._display.BLACK,
      self._display.YELLOW: self._display.BLACK,
      self._display.GREEN:  self._display.BLACK,
      self._display.BLUE:   self._display.WHITE,
      self._display.ORANGE: self._display.BLACK,
      }

  # --- read settings from config-file   -------------------------------------

  def _read_settings(self):
    """ read settings from /etc/pi-e-ink-daily.json """

    if os.path.exists(CONFIG_FILE_DEFAULT):
      with open(CONFIG_FILE_DEFAULT,"r") as f:
        self._opts.update(json.load(f))
    if os.path.exists(CONFIG_FILE):
      with open(CONFIG_FILE,"r") as f:
        self._opts.update(json.load(f))

  # --- create color-maps   --------------------------------------------------

  def _map_colors(self):
    """ map colors """

    options = vars(self._opts)
    for opt in options:
      if '_COLOR' in opt:
        key = options[opt]
        if key in self._cmap:
          options[opt] = self._cmap[options[opt]]
        else:
          options[opt] = self._cmap['black']

  # --- create fonts   -----------------------------------------------------

  def _create_fonts(self):
    """ create fonts """

    self._title_font  = ImageFont.truetype(self._opts.TITLE_FONT,
                                          self._opts.TITLE_SIZE)
    self._day_font    = ImageFont.truetype(self._opts.DAY_FONT,
                                          self._opts.DAY_SIZE)
    self._time_font   = ImageFont.truetype(self._opts.TIME_FONT,
                                          self._opts.TIME_SIZE)
    self._text_font   = ImageFont.truetype(self._opts.TEXT_FONT,
                                          self._opts.TEXT_SIZE)
    self._status_font = ImageFont.truetype(self._opts.STATUS_FONT,
                                          self._opts.STATUS_SIZE)

  # --- draw a line   ------------------------------------------------------

  def _draw_hline(self,y):
    """ draw a horizontal line """

    self._canvas.line([(0,y),(self._opts.WIDTH,y)],
                                  fill=self._opts.LINE_COLOR,width=1)

  # --- main title   -------------------------------------------------------

  def draw_title(self):
    """ Draw title """

    if self._opts.TITLE:
      if self._opts.TITLE[0] == "%":
        title = datetime.datetime.now().strftime(self._opts.TITLE)
      else:
        title = self._opts.TITLE
    else:
      title = datetime.datetime.now().strftime("%B")  # month

    self._canvas.text((20,20),title,
                      font=self._title_font,
                      fill=self._opts.TITLE_COLOR)

  # --- day box upper right   ------------------------------------------------

  def draw_day(self):
    """ draw box with current day of the month """

    day         = str(datetime.date.today().day)
    day_size    = self._canvas.textsize(day,self._day_font,spacing=0)
    day_topleft = (self._opts.WIDTH-day_size[0]-self._opts.MARGINS[0],0)
    day_box_y   = day_size[1]+2*self._opts.MARGINS[3]+1
    day_box     = [day_topleft[0]-self._opts.MARGINS[0],0,
                   self._opts.WIDTH+1,day_box_y]

    if datetime.date.today().weekday() == 6:
      self._canvas.rectangle(day_box,fill=self._opts.DAY_COLOR_BG7)
    else:
      self._canvas.rectangle(day_box,fill=self._opts.DAY_COLOR_BG)
    self._canvas.text(day_topleft,day,font=self._day_font,
                      fill=self._opts.DAY_COLOR)
    self._draw_hline(day_box_y)

    # update global y offset
    self._y_off = day_box_y + 2

  # --- overlay image   -----------------------------------------------------

  def draw_image(self,path):
    """ draw image """

    # load image
    try:
      image = Image.open(path)
      x_off = int((self._opts.WIDTH - image.width)/2)
      y_off = self._y_off + int((self._opts.HEIGHT - self._y_off -
               self._opts.HEIGHT_S - image.height)/2)
      self._image.paste(image,box=(x_off,y_off))
      image.close()
    except:
      traceback.print_exc()
      return

  # --- status line   -------------------------------------------------------

  def draw_status(self):
    """ draw status-line and text """

    status_y = self._opts.HEIGHT - self._opts.HEIGHT_S
    self._draw_hline(status_y)

    # update-info
    status_text = "Updated: %s" % datetime.datetime.now().strftime("%x %X")
    self._canvas.text((self._opts.MARGINS[2],status_y),
                      status_text,
                      font=self._status_font,
                      fill=self._opts.STATUS_COLOR)

    # battery-info
    if inky_available:
      import RPi.GPIO as GPIO
      GPIO.setmode(GPIO.BCM)
      if self._opts.BAT_OK_VALUE:
        pull = GPIO.PUD_UP
      else:
        pull = GPIO.PUD_DOWN
      GPIO.setup(self._opts.BAT_GPIO,GPIO.IN,pull_up_down=pull)

      if GPIO.input(self._opts.BAT_GPIO) == self._opts.BAT_OK_VALUE:
        bat_text  = self._opts.BAT_OK_TEXT
        bat_color = self._opts.BAT_OK_COLOR
      else:
        bat_text  = self._opts.BAT_LOW_TEXT
        bat_color = self._opts.BAT_LOW_COLOR
    else:
      # just simulate
      if self._opts.BAT_OK_VALUE:
        bat_text  = self._opts.BAT_OK_TEXT
        bat_color = self._opts.BAT_OK_COLOR
      else:
        bat_text  = self._opts.BAT_LOW_TEXT
        bat_color = self._opts.BAT_LOW_COLOR

    bat_size  = self._canvas.textsize(bat_text,self._status_font,spacing=0)
    self._canvas.text((self._opts.WIDTH-self._opts.MARGINS[3]-bat_size[0],
                       status_y),
                      bat_text,
                      font=self._status_font,
                      fill=bat_color)

  # --- show image   ---------------------------------------------------------

  def show(self):
    """ show current screen on device """

    if inky_available:
      try:
        self._display.set_border(self._opts.BORDER_COLOR)
        self._display.set_image(self._image)
        self._display.show()
      except:
        traceback.print_exc()
        self.rc = 3
      return

    # fallback to direct display using PIL default viewer
    self._image.show()

# --- main program   ----------------------------------------------------------

if __name__ == '__main__':
  locale.setlocale(locale.LC_ALL, '')

  screen = DailyAgenda()
  screen.draw_title()
  screen.draw_day()

  screen.provider.draw_content()

  screen.draw_status()
  screen.show()
  if screen._opts.no_shutdown_on_error and screen.rc > 0:
    sys.exit(screen.rc)
  elif screen._opts.auto_shutdown:
    sys.exit(0)
  else:
    sys.exit(1)
