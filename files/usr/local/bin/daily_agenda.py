#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# TODO: font-sizes -> options
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

CONFIG_FILE = "/etc/pi-e-ink-daily.json"

# --- system-imports   -------------------------------------------------------

import argparse
import sys, os, datetime, locale, json
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
# --- main application class   -----------------------------------------------

class DailyAgenda(object):
  """ main application class """

  # --- constructor   --------------------------------------------------------

  def __init__(self):

    # default options
    self._options = {
      "WIDTH"      : 400,         # screen width
      "HEIGHT"     : 300,         # screen height
      "HEIGHT_E"   :  40,         # height of agenda entry
      "HEIGHT_S"   :  19,         # offset from bottom of status line
      "MARGINS"    : (5,5,5,5),   # (top,bottom,left,right)

      "TITLE"      : "Daily Agenda",
      "TITLE_FONT" : "/usr/share/fonts/truetype/DejaVuSans-BoldOblique.ttf",
      "TITLE_COLOR": 0,


      "DAY_FONT"   : "/usr/share/fonts/truetype/DejaVuSerif-Bold.ttf",
      "DAY_COLOR"  : 255,
      "DAY_COLOR_BG" : 128,

      "TEXT_FONT"  : "/usr/share/fonts/truetype/DejaVuSerif.ttf",
      "TEXT_COLOR" : 0,
      "TEXT_COLOR_I" : 255,
      "TEXT_COLOR_BG" : 192,

      "LINE_COLOR" : 64
      }

    self._read_settings()
    self._create_fonts()

    # application objects
    self._image  = Image.new("L",
                             (self._options["WIDTH"],self._options["HEIGHT"]),
                             255)
    self._canvas = ImageDraw.Draw(self._image)
    self._y_off  = 0

  # --- read settings from config-file   -------------------------------------

  def _read_settings(self):
    """ read settings from /etc/pi-e-ink-daily.json """

  if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE,"r") as f:
      self._options = json.load(f)

  # --- create fonts   -----------------------------------------------------

  def _create_fonts(self):
    """ create fonts """

    self._title_font = ImageFont.truetype(self._options["TITLE_FONT"],35)
    self._day_font   = ImageFont.truetype(self._options["DAY_FONT"],60)
    self._time_font  = ImageFont.truetype(self._options["TEXT_FONT"],30)
    self._text_font  = ImageFont.truetype(self._options["TEXT_FONT"],15)

  # --- draw a line   ------------------------------------------------------

  def _draw_hline(self,y):
    """ draw a horizontal line """

    self._canvas.line([(0,y),(self._options["WIDTH"],y)],
                                  fill=self._options["LINE_COLOR"],width=1)

  # --- main title   -------------------------------------------------------

  def draw_title(self):
    """ Draw title """

    self._canvas.text((20,20),self._options["TITLE"],
                      font=self._title_font,
                      fill=self._options["TITLE_COLOR"])

  # --- day box upper right   ------------------------------------------------

  def draw_day(self):
    """ draw box with current day of the month """

    day         = str(datetime.date.today().day)
    day_size    = self._canvas.textsize(day,self._day_font,spacing=0)
    day_topleft = (self._options["WIDTH"]-day_size[0]-self._options["MARGINS"][0],0)
    day_box_y   = day_size[1]+2*self._options["MARGINS"][3]+1
    day_box     = [day_topleft[0]-self._options["MARGINS"][0],0,
                   self._options["WIDTH"]+1,day_box_y]

    self._canvas.rectangle(day_box,fill=self._options["DAY_COLOR_BG"])
    self._canvas.text(day_topleft,day,font=self._day_font,
                      fill=self._options["DAY_COLOR"])
    self._draw_hline(day_box_y)

    # update global y offset
    self._y_off = day_box_y + 2

  # --- agenda entry   ------------------------------------------------------

  def draw_entry(self,e_time,e_text,shade=False):
    """ draw a single agenda entry """

    # background
    text_color = self._options["TEXT_COLOR"]
    if shade:
      background = [(0,self._y_off+1),
                    (self._options["WIDTH"],
                                    self._y_off+self._options["HEIGHT_E"]+1)]
      self._canvas.rectangle(background,
                             fill=self._options["TEXT_COLOR_BG"])
      text_color = self._options["TEXT_COLOR_I"]
  
    # time-value
    time_size = self._canvas.textsize(e_time,self._time_font,spacing=0)
    self._canvas.text((self._options["MARGINS"][2],self._y_off),
                      e_time,font=self._time_font,
                      fill=self._options["TEXT_COLOR"])

    # text (2 lines)
    txt_x_off = self._options["MARGINS"][2] + time_size[0] + 4
    txt_y_off = self._y_off + 2
    text_size = self._canvas.textsize(e_text[0],
                                      self._text_font,spacing=0)
    self._canvas.text((txt_x_off,txt_y_off),e_text[0],
                      font=self._text_font,
                      fill=self._options["TEXT_COLOR"])

    txt_y_off += text_size[1]
    self._canvas.text((txt_x_off,txt_y_off),
                      e_text[1],font=self._text_font,
                      fill=self._options["TEXT_COLOR"])

    # ending line
    self._y_off += self._options["HEIGHT_E"] + 2
    self._draw_hline(self._y_off)

    print("y_off: %d" % self._y_off)

  # --- status line   -------------------------------------------------------

  def draw_status(self):
    """ draw status-line and text """

    status_y = self._options["HEIGHT"] - self._options["HEIGHT_S"]
    self._draw_hline(status_y)

    status_text = "Updated: %s" % datetime.datetime.now().strftime("%x %X")
    self._canvas.text((self._options["MARGINS"][2],status_y+2),
                      status_text,
                      font=self._text_font,
                      fill=self._options["TEXT_COLOR"]) 

  # --- show image   ---------------------------------------------------------

  def show(self):
    """ show current screen on device """

    self._image.show()

# --- main program   ----------------------------------------------------------

if __name__ == '__main__':
  locale.setlocale(locale.LC_ALL, '')

  screen = DailyAgenda()
  screen.draw_title()
  screen.draw_day()
  for i in range(5):
    screen.draw_entry("12:33",["Wichtiger Termin","Nr. %d" % i],i%2)
  screen.draw_status()
  screen.show()
