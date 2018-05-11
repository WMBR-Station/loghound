#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import datetime
import json
import codecs
import model

def parseSchedule(sched_raw,today,numdays):
  timestrtodelta = lambda timestr: datetime.timedelta(0, sum(map(lambda x,y: int(x)*y, timestr.split(":"), [60*60,60])))
  dates = [today + datetime.timedelta(i) for i in xrange(numdays)]
  progEvents = dict([(date,[]) for date in dates])
  opEvents = dict([(date,[]) for date in dates])

  schedule = json.loads(sched_raw)
  if "error" in schedule:
    raise(Exception("Error in Retrieving Program Schedule",schedule["error"]))

  for date_str in schedule:
    year  = int(date_str.split("-")[0])
    month = int(date_str.split("-")[1])
    day   = int(date_str.split("-")[2])
    date = datetime.datetime(year,month,day)
    for show in schedule[date_str]:

      if not date in progEvents:
        mindate,maxdate = min(progEvents.keys()),max(progEvents.keys())
        raise Exception("The programming log date <%s> cannot be used to generate the date range <%s, %s>" % (date,mindate,maxdate))

      if not date in opEvents:
        mindate,maxdate = min(opEvents.keys()),max(opEvents.keys())
        raise Exception("The programming log date <%s> cannot be used to generate the date range <%s, %s>" % (date,mindate,maxdate))

      if show["type"] == "show":
         progEvents[date].append(model.show(
          show["show_name"],
          date+timestrtodelta(show["start_time"]),
          date+timestrtodelta(show["end_time"]),
          show["engineer"],
          show["producers"],
          show["announcers"]))

      elif show["type"] == "signoff":
        opEvents[date].append((date+timestrtodelta(show["time"]),
                               'TURN OFF TRANSMITTER'))
        progEvents[date].append(model.signoff(date+timestrtodelta(show["time"])))
      elif show["type"] == "signon":
        opEvents[date].append((date+timestrtodelta(show["time"]),
                               'TEST EAS LIGHTS AND TURN ON TRANSMITTER'))
        progEvents[date].append(model.signon(date+timestrtodelta(show["time"])))

  return progEvents,opEvents



def getSchedule(printcmd,source,today,numdays):
  # SECOND, download the schedule
  # TODO: get rid of this and just talk to the database or whatever directly if
  #       that's at all possible!  This is a little silly!  If we're going to
  #       output things this way, we should put out an XML file!
  phpquery = 'templogs.php?start_year=%d&start_month=%d&start_day=%d&num_days=%d'
  local_url = 'http://localhost/%s' % phpquery
  web_url = 'http://www.wmbr.org/~lowe/%s' % phpquery



  if source == "web-live":
    printcmd("Downloading schedule...")
    url = web_url % (today.year,today.month,today.day,numdays)
    printcmd("URL: %s" % url)
    sched_raw = unicode(urllib.urlopen(url).read(), "iso-8859-1")

  elif source == "web-local":
    printcmd("Downloading schedule...")
    url = local_url % (today.year,today.month,today.day,numdays)
    printcmd("URL: %s" % url)
    sched_raw = unicode(urllib.urlopen(url).read(), "iso-8859-1")

  elif source == "local":
    if args.input is None:
       raise Exception("[error] must specify input file if local source is selected")

    printcmd("Loading schedule from local file...")
    sched_raw = "".join(codecs.open(args.input, "r", encoding='iso-8859-1').readlines())
    printcmd("Done.\n")

  return sched_raw

def load(printcmd,source,today,numdays):
    sched_raw = getSchedule(printcmd,source,today,numdays)
    progevents,opevents = parseSchedule(sched_raw,today,numdays)
    return progevents,opevents
