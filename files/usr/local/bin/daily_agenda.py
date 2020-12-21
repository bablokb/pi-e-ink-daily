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
from operator import itemgetter

from PIL import Image, ImageDraw, ImageFont
import caldav
import tzlocal

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

    self._create_color_maps()     # create color-maps
    self._read_settings()         # creates self._opts
    self.rc = 0                   # return-code
    self._create_fonts()

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
    self._y_off  = 0

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

  # --- read settings from config-file   -------------------------------------

  def _read_settings(self):
    """ read settings from /etc/pi-e-ink-daily.json """

    if os.path.exists(CONFIG_FILE_DEFAULT):
      with open(CONFIG_FILE_DEFAULT,"r") as f:
        options = json.load(f)
    if os.path.exists(CONFIG_FILE):
      with open(CONFIG_FILE,"r") as f:
        options.update(json.load(f))

    for opt in options:
      if '_COLOR' in opt:
        key = options[opt]
        if key in self._cmap:
          options[opt] = self._cmap[options[opt]]
        else:
          options[opt] = self._cmap['black']

    # convert to attributes
    self._opts = Options(options)

    # path to images
    pgm_dir = os.path.dirname(os.path.realpath(__file__))
    img_dir = os.path.realpath(os.path.join(pgm_dir,"..",
                                            "share","pi-e-ink-daily"))

    self.NO_CONNECT = os.path.join(img_dir,self._opts.no_server_connection)
    self.NO_EVENTS  = os.path.join(img_dir,self._opts.no_events)

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

  # --- return maximal number of possible entries   ------------------------

  def get_max_entries(self):
    """ return entries - must be called after dray_day """

    return int((self._opts.HEIGHT-self._opts.HEIGHT_S-self._y_off)/self._opts.HEIGHT_E)

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

  # --- agenda entry   ------------------------------------------------------

  def draw_entry(self,e_time,e_text,e_color):
    """ draw a single agenda entry """

    # background
    background = [(0,self._y_off+1),
                    (self._opts.WIDTH,
                                    self._y_off+self._opts.HEIGHT_E-1)]
    self._canvas.rectangle(background,fill=e_color)
  
    # time-value
    tm      = e_time.split('-')
    tm_size = [0,0]
    tm_size[0] = self._canvas.textsize(tm[0],self._time_font,spacing=0)
    tm_size[1] = self._canvas.textsize(tm[1],self._time_font,spacing=0)
    if e_time != "00:00-23:59":
      # only print time for none full-day events
      self._canvas.text((self._opts.MARGINS[2],self._y_off+2),
                        tm[0],font=self._time_font,
                        fill=self._opts.TIME_COLOR)
      self._canvas.text((self._opts.MARGINS[2],self._y_off+4+tm_size[0][1]),
                        tm[1],font=self._time_font,
                        fill=self._opts.TIME_COLOR)

    # text (2 lines)
    txt_x_off = self._opts.MARGINS[2] + max(tm_size[0][0],tm_size[1][0]) + 4
    txt_y_off = self._y_off + 2
    text_size = self._canvas.textsize(e_text[0],
                                      self._text_font,spacing=0)
    self._canvas.text((txt_x_off,txt_y_off),e_text[0],
                      font=self._text_font,
                      fill=self._opts.TEXT_COLOR)

    txt_y_off += text_size[1]
    self._canvas.text((txt_x_off,txt_y_off),
                      e_text[1],font=self._text_font,
                      fill=self._opts.TEXT_COLOR)

    # ending line
    self._y_off += self._opts.HEIGHT_E
    self._draw_hline(self._y_off)

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

    status_text = "Updated: %s" % datetime.datetime.now().strftime("%x %X")
    self._canvas.text((self._opts.MARGINS[2],status_y+2),
                      status_text,
                      font=self._status_font,
                      fill=self._opts.STATUS_COLOR)

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

  # --- read agendas from caldav-servers   ------------------------------------

  def get_agenda(self):
    """ read agenda for all configured calendars """

    entries = []
    for cal_info in self._opts.cals:
      self._get_agenda_for_cal(cal_info,entries)
    entries.sort(key=itemgetter(0))
    return entries

  # --- read agenda from caldav-server   --------------------------------------

  def _get_agenda_for_cal(self,cal_info,entries):
    """ read agenda from caldav-server """

    start_of_day = datetime.datetime.combine(datetime.date.today(),
                                         datetime.time.min)
    end_of_day   = datetime.datetime.combine(datetime.date.today(),
                                         datetime.time.max)
    now          = tzlocal.get_localzone().localize(datetime.datetime.now())

    client = caldav.DAVClient(url=cal_info["dav_url"],
                                username=cal_info["dav_user"],
                                password=cal_info["dav_pw"])

    # get calendar by name
    calendars = client.principal().calendars()
    cal = next(c for c in calendars if c.name == cal_info["cal_name"])

    # extract relevant data
    cal_events = cal.date_search(start=start_of_day,end=end_of_day,expand=True)
    agenda_list = []
    for cal_event in cal_events:
      item = {}
      if hasattr(cal_event.instance, 'vtimezone'):
        tzinfo = cal_event.instance.vtimezone.gettzinfo()
      else:
        tzinfo = tzlocal.get_localzone()
      components = cal_event.instance.components()
      for component in components:
        if component.name != 'VEVENT':
          continue
        item['dtstart'] = self._get_timeattr(
          component,'dtstart',start_of_day,tzinfo)
        if hasattr(component,'duration'):
          duration = getattr(component,'duration').value
          item['dtend'] = item['dtstart'] + duration
        else:
          item['dtend']   = self._get_timeattr(
            component,'dtend',end_of_day,tzinfo)
        if item['dtend'] < now:
          # ignore old events
          continue
        if item['dtend'].day != item['dtstart'].day:
          item['dtend'] = tzlocal.get_localzone().localize(end_of_day)

        for attr in ('summary', 'location'):
          if hasattr(component,attr):
            item[attr] = getattr(component,attr).value
          else:
            item[attr] = ""
        agenda_list.append(item)

    for item in agenda_list:
      entries.append(("%s-%s" % (item['dtstart'].astimezone().strftime("%H:%M"),
                                 item['dtend'].astimezone().strftime("%H:%M")),
                      (item['summary'],item['location']),
                      self._cmap[cal_info["cal_color"]]))

  # --- extract time attribute   ----------------------------------------------

  def _get_timeattr(self,component,timeattr,default,tzinfo):
    """ extract time attribute """

    if hasattr(component,timeattr):
      dt = getattr(component,timeattr).value
      if not isinstance(dt,datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day)
    else:
      dt = default
    if not dt.tzinfo:
      dt = tzinfo.localize(dt)
    return dt

# --- main program   ----------------------------------------------------------

if __name__ == '__main__':
  locale.setlocale(locale.LC_ALL, '')

  screen = DailyAgenda()
  screen.draw_title()
  screen.draw_day()

  try:
    entries = screen.get_agenda()
  except:
    traceback.print_exc()
    screen.rc = 3

  if screen.rc:
    screen.draw_image(screen.NO_CONNECT)
  elif len(entries):
    count = 0
    for entry in entries:
      screen.draw_entry(*entry)
      count += count
      if count > screen.get_max_entries():
        break
  else:
    screen.draw_image(screen.NO_EVENTS)

  screen.draw_status()
  screen.show()
  if screen._opts.no_shutdown_on_error and screen.rc > 0:
    sys.exit(screen.rc)
  else:
    sys.exit(0)
