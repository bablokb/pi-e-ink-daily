#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pi-e-ink-daily: daily agenda on a wHat e-ink display
#
# Content-provider for the daily agenda
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-e-ink-daily
#
# ----------------------------------------------------------------------------

import caldav
import tzlocal
import datetime
import traceback
from operator import itemgetter

from ContentProvider import ContentProvider

class CalContentProvider(ContentProvider):

  # --- constructor   --------------------------------------------------------
  
  def __init__(self,screen):
    super(CalContentProvider,self).__init__(screen)

  # --- return maximal number of possible entries   ------------------------

  def get_max_entries(self):
    """ return entries - must be called after dray_day """

    return int((self.opts.HEIGHT-
                self.opts.HEIGHT_S-self.screen._y_off)/
                                                    self.opts.HEIGHT_E)

  # --- read agendas from caldav-servers   ------------------------------------

  def _get_agenda(self):
    """ read agenda for all configured calendars """

    entries = []
    for cal_info in self.opts.cals:
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
                      self.screen._cmap[cal_info["cal_color"]]))

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

  # --- agenda entry   ------------------------------------------------------

  def _draw_entry(self,e_time,e_text,e_color):
    """ draw a single agenda entry """

    # background
    background = [(0,self.screen._y_off+1),
                    (self.opts.WIDTH,
                                    self.screen._y_off+self.opts.HEIGHT_E-1)]
    self.canvas.rectangle(background,fill=e_color)
  
    # time-value
    tm      = e_time.split('-')
    tm_size = [0,0]
    tm_size[0] = self.canvas.textsize(tm[0],self.screen._time_font,spacing=0)
    tm_size[1] = self.canvas.textsize(tm[1],self.screen._time_font,spacing=0)
    if e_time != "00:00-23:59":
      # only print time for none full-day events
      self.canvas.text((self.opts.MARGINS[2],self.screen._y_off+2),
                        tm[0],font=self.screen._time_font,
                        fill=self.screen._bg_map[e_color])
      self.canvas.text((self.opts.MARGINS[2],self.screen._y_off+4+tm_size[0][1]),
                        tm[1],font=self.screen._time_font,
                        fill=self.screen._bg_map[e_color])

    # text (2 lines)
    txt_x_off = self.opts.MARGINS[2] + max(tm_size[0][0],tm_size[1][0]) + 4
    txt_y_off = self.screen._y_off + 2
    text_size = self.canvas.textsize(e_text[0],
                                      self.screen._text_font,spacing=0)
    self.canvas.text((txt_x_off,txt_y_off),e_text[0],
                      font=self.screen._text_font,
                      fill=self.screen._bg_map[e_color])

    txt_y_off += text_size[1]
    self.canvas.text((txt_x_off,txt_y_off),
                      e_text[1],font=self.screen._text_font,
                      fill=self.screen._bg_map[e_color])

    # ending line
    self.screen._y_off += self.opts.HEIGHT_E
    self.screen._draw_hline(self.screen._y_off)

  # --- draw content on screen   ---------------------------------------------

  def draw_content(self):
    """ draw agenda-items """

    try:
      entries = self._get_agenda()
    except:
      traceback.print_exc()
      self.screen.rc = 3

    if self.screen.rc:
      self.screen.draw_image(self.screen.NO_CONNECT)
    elif len(entries):
      count = 0
      for entry in entries:
        self._draw_entry(*entry)
        count += count
        if count > self.get_max_entries():
          break
    else:
      self.screen.draw_image(screen.NO_EVENTS)

