#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: Inky-Impression test-program
#
# This code displays a string, iterating all colors for background and
# foreground.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

import traceback

# --- system-imports   -------------------------------------------------------

import argparse
import sys, os, datetime, locale, json
from operator import itemgetter

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
  def __init__(self):
    pass

# ----------------------------------------------------------------------------
# --- main application class   -----------------------------------------------

class ColorTester(object):
  """ main application class """

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    global inky_available
    if inky_available:
      try:
        self._display = auto()
      except Exception:
        # traceback.print_exc()
        inky_available = False

    # add some attributes to simulated object
    if not inky_available:
      self._display = Options()
      self._display.width  = 600
      self._display.height = 448
      self._display.WHITE  = (255,255,255)
      self._display.BLACK  = (0,0,0)
      self._display.RED    = (255,0,0)
      self._display.YELLOW = (255,255,0)
      self._display.GREEN  = (0,128,0)
      self._display.BLUE   = (0,0,255)
      self._display.ORANGE = (255,165,0)

    # application objects
    if inky_available:
      self._image  = Image.new("P",
                             (self._display.width,self._display.height),
                             color=self._display.WHITE)
    else:
      self._image  = Image.new("RGB",
                             (self._display.width,self._display.height),
                              color=self._display.WHITE)
    self._canvas = ImageDraw.Draw(self._image)

    # font and text
    self._font   = ImageFont.truetype(
      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",50)
    self._text = "\u03C0"
    self._text_size = self._canvas.textsize(self._text,self._font,spacing=0)

    # colors
    self._colors = [
      self._display.WHITE,
      self._display.BLACK,
      self._display.RED,
      self._display.YELLOW,
      self._display.GREEN,
      self._display.BLUE,
      self._display.ORANGE
      ]

  # --- day box upper right   ------------------------------------------------

  def _draw_box(self,x,y,fg,bg):
    """ draw box with at given position """

    box = [x,y,x+self._box_length,y+self._box_length]
    self._canvas.rectangle(box,fill=bg)
    self._canvas.text([x+self._text_x_off,y+self._text_y_off],self._text,
                      font=self._font,fill=fg)

  # --- draw color boxes   ---------------------------------------------------

  def draw_colors(self):
    """ draw fg/bg boxes """

    self._box_length = int(self._display.height/len(self._colors))
    self._text_x_off = int( (self._box_length-self._text_size[0])/2 )
    self._text_y_off = int( (self._box_length-self._text_size[1])/2 )
    y_off = 0
    for fg_color in self._colors:
      x_off = 0
      for bg_color in self._colors:
        self._draw_box(x_off,y_off,fg_color,bg_color)
        x_off += self._box_length
      y_off += self._box_length
      self._canvas.line([(0,y_off-1),(x_off,y_off-1)],
                                  fill=self._display.BLACK,width=1)


  # --- show image   ---------------------------------------------------------

  def show(self):
    """ show image """

    if inky_available:
      try:
        self._display.set_border(self._display.WHITE)
        self._display.set_image(self._image)
        self._display.show()
      except:
        traceback.print_exc()
      return

    # fallback to direct display using PIL default viewer
    self._image.show()

# --- main program   ----------------------------------------------------------

if __name__ == '__main__':
  locale.setlocale(locale.LC_ALL, '')

  screen = ColorTester()
  screen.draw_colors()
  screen.show()
