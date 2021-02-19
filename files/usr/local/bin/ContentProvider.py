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

import os, json

class ContentProvider(object):

  CONFIG_FILE_DEFAULT = "/etc/pi-e-ink-daily.{}.defaults.json"

  # --- constructor   --------------------------------------------------------
  
  def __init__(self,screen):
    """ save screen object """
    self.screen = screen
    self.opts   = screen._opts

  # --- read default settings for content-provider   -------------------------

  def read_settings(self):
    """ read settings """

    config_file = ContentProvider.CONFIG_FILE_DEFAULT.format(
                                                      self.__class__.__name__)
    if os.path.exists(config_file):
      with open(config_file,"r") as f:
        self.opts.update(json.load(f))

  # --- set canvas-property   ------------------------------------------------

  def set_canvas(self,canvas):
    self.canvas = canvas

  # --- draw content on screen   ---------------------------------------------

  def draw_content(self):
    """ draw content - must be implemented by subclasses """
    raise NotImplementedError
