#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# Base class for content-providers
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

class ContentProvider(object):

  # --- constructor   --------------------------------------------------------
  
  def __init__(self,screen):
    """ save screen object """
    self.screen = screen
    self.opts   = screen._opts

  # --- set canvas-property   ------------------------------------------------

  def set_canvas(self,canvas):
    self.canvas = canvas

  # --- draw content on screen   ---------------------------------------------

  def draw_content(self):
    """ draw content - must be implemented by subclasses """
    raise NotImplementedError
