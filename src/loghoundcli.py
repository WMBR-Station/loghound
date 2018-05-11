#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse 
import urllib
import codecs
import model
import json
import calendar
import datetime
import random
import twilight

import os
from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate, Table, TableStyle, Paragraph, flowables
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
import tablegen
import progtablegen
import sys
import calendar
import numpy as np


def generateLog(logEvents,today,numdays,location='.',oplog=True,add_blanks=False):
  #letter paper
  dates = [today + datetime.timedelta(i) for i in xrange(numdays)]
  
  PAGE_WIDTH, PAGE_HEIGHT = letter
  styles=getSampleStyleSheet()
  Elements=[]
  
  def foot(title):
    def _foot(canvas, doc):
      today = datetime.date(doc.docEval("currentYear"), doc.docEval("currentMonth"), doc.docEval("currentDay"))
      canvas.saveState()
      canvas.setFont('Times-Roman',20)
      canvas.drawString(0.3*inch, PAGE_HEIGHT-0.7*inch, title)
      canvas.drawRightString(PAGE_WIDTH-0.5*inch, PAGE_HEIGHT-0.7*inch, today.strftime("%A, %b %d, %Y"))
      # this draws the page number on the outside corner of the log
      if doc.page % 2 == 0:
        canvas.drawString(0.3*inch, 0.3*inch, "Page %d" % (doc.page))
      else:
        canvas.drawRightString(PAGE_WIDTH-0.5*inch, 0.3*inch, "Page %d" % (doc.page))
      canvas.restoreState()
    return _foot
  
  def title(title):
    def _title(canvas,doc):
      canvas.saveState()
      canvas.setFont('Times-Roman',20)
      canvas.drawString(0.3*inch, PAGE_HEIGHT-0.7*inch, title)
      canvas.drawRightString(PAGE_WIDTH-0.5*inch, PAGE_HEIGHT-0.7*inch, "%02d/%02d/%d — %02d/%02d/%d" % (dates[0].month, dates[0].day, dates[0].year, dates[-1].month, dates[-1].day, dates[-1].year))
      canvas.restoreState()
    return _title
  
  def rulesPage():
    import op_title

    eltList = []
    paraPrefix = "<para";
    for elt in op_title.contents.split(paraPrefix):
      if len(elt.strip()) > 0:
        eltList.append(Paragraph(paraPrefix + elt, styles['Normal']))
    data = [
        ["Brian Sennett", "", "Cell: 845-891-4649"],
        ["Ted Young",      "Home: 617-776-7473", "Cell: 617-447-8439"] ]
    eltList.append(Table(data, style=[('SIZE',(0,0),(-1,-1),12)]))
    return eltList
  
  def SigPage():
    data = [ ["CUSTODIAN (print name)",
              "INITIALS",
              "TIME ON",
              "SIGNATURE",
              "TIME OFF",
              "SIGNATURE"]
           ] + [[None]*6]*22
    tableWidths = [2*inch,None,None,1.7*inch,None,1.7*inch]
    tableHeights = [None] + [30]*22
    t = Table(data, tableWidths, tableHeights)
    t.setStyle(TableStyle([
          ('VALIGN', (0,0), (-1,0), 'TOP'),
          ('ALIGN', (0,0), (-1,0), 'CENTER'),
          ('ALIGN', (3,0), (3,0), 'RIGHT'),
          ('ALIGN', (5,0), (5,0), 'RIGHT'),
          ('GRID', (0,0), (1,-1), .6, colors.black),
          ('LINEABOVE', (2,0), (3,-1), .6, colors.black),
          ('LINEAFTER', (3,0), (3,-1), .6, colors.black),
          ('LINEABOVE', (4,0), (5,-1), .6, colors.black),
          ('LINEAFTER', (5,0), (5,-1), .6, colors.black),
          ('BOX',(0,0),(-1,-1),2,colors.black),
          ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
          ('VALIGN', (0,1), (0, -1), 'MIDDLE'),
      ]))
    return t

  ## The operating log

  printcmd("Writing operating log...")

  if oplog:
	  doc = BaseDocTemplate(location+"/oplog.pdf",showBoundary=0,allowSplitting=0,leftMargin=0.5*inch,rightMargin=0.5*inch,topMargin=1.4*inch,bottomMargin=0.5*inch)

	  frameNormal = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')

	  Elements.extend(rulesPage())

	  for date in dates:
	    Elements.append(flowables.DocAssign("currentYear",  date.year))
	    Elements.append(flowables.DocAssign("currentMonth", date.month))
	    Elements.append(flowables.DocAssign("currentDay",   date.day))
	    tables = tablegen.make_day_tables(logEvents[date])
	    Elements.append(NextPageTemplate('OTALogPage'))
	    Elements.append(PageBreak())
	    Elements.append(SigPage())
	    for table in tables:
	      Elements.append(NextPageTemplate('OpLogPage'))
	      Elements.append(PageBreak())
	      Elements.append(table)

	  doc.addPageTemplates([PageTemplate(id='Title',frames=frameNormal,onPage=title("WMBR Operating Log"),pagesize=letter),
				PageTemplate(id='OTALogPage',frames=frameNormal,onPage=foot("WMBR Operating Log"),pagesize=letter),
				PageTemplate(id='OpLogPage',frames=frameNormal,onPage=foot("WMBR Operating Log"),pagesize=letter)
				])
  else:
	  printcmd("Writing programming log...")
	  doc = BaseDocTemplate(location+"/proglog.pdf",showBoundary=0,allowSplitting=0,leftMargin=0.5*inch,rightMargin=0.5*inch,topMargin=1.4*inch,bottomMargin=0.5*inch)
	  
	  frameNormal = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
	  
	  Elements.extend(rulesPage())
	  
	  for date in dates:
	    Elements.append(flowables.DocAssign("currentYear",  date.year))
	    Elements.append(flowables.DocAssign("currentMonth", date.month))
	    Elements.append(flowables.DocAssign("currentDay",   date.day))
	    tables = progtablegen.make_day_tables(logEvents[date],add_blanks=add_blanks)
	   
            Elements.append(NextPageTemplate('OTALogPage'))
	    Elements.append(PageBreak())
	    Elements.append(SigPage())
	    Elements.append(NextPageTemplate('ProgLogPage'))
	    Elements.append(PageBreak())
	    Elements.extend(tables)
	  
	  doc.addPageTemplates([PageTemplate(id='Title',frames=frameNormal,onPage=title("WMBR Programming Log"),pagesize=letter),
				PageTemplate(id='OTALogPage',frames=frameNormal,onPage=foot("WMBR Programming Log"),pagesize=letter),
				PageTemplate(id='ProgLogPage',frames=frameNormal,onPage=foot("WMBR Programming Log"),pagesize=letter)
				])
  
  #start the construction of the pdf
  doc.build(Elements)
  

def generateProgLog(progEvents,today,numdays,location='.',add_blanks=False):
   generateLog(progEvents,today,numdays,location='.',oplog=False,add_blanks=add_blanks)

def generateOpLog(opEvents,today,numdays,location='.'):
   generateLog(opEvents,today,numdays,location='.',oplog=True) 

def computeAltShows(lastProgLog,currProgLog):
  alternating = {}
  for day in currProgLog:
     lastday = day - datetime.timedelta(days=7)
     currShows = filter(lambda x : isinstance(x,model.show), currProgLog[day])
     lastShows = filter(lambda x : isinstance(x,model.show), lastProgLog[lastday])

     currShowDict = dict(map(lambda x: (x.start().hour,x), currShows))
     lastShowDict = dict(map(lambda x: (x.start().hour,x), lastShows))
     for date in currShowDict.keys():
        if date in lastShowDict.keys():
            name1 = currShowDict[date].name
            name2 = lastShowDict[date].name 
            if name1 != name2:
               alternating[name1] = True
               alternating[name2] = True

  for day in currProgLog:
     for show in currProgLog[day]:
        if isinstance(show,model.show) and show.name in alternating:
           show.alternates(alternating[show.name])

  return currProgLog

def insertFCCEvents(opEvents,today,numdays):

   def get_week(date):
     weeks = np.array(calendar.monthcalendar(date.year,date.month))
     week = np.where(weeks==date.day)[0][0] + 1
     return week

   dates = [today + datetime.timedelta(i) for i in xrange(numdays)]
   # which dates should have an EAS test?

   weeks = map(lambda d: get_week(d), dates)
   by_week = {}
   SUNDAY = 6
   for weekno,date in zip(weeks,dates):
     if not weekno in by_week:
       by_week[weekno] = []

     if date.weekday() != SUNDAY:
       by_week[weekno].append(date)

   easDays = []
   for days in by_week.values():
     easDays.append(random.sample(days,1)[0])

   # check the tower lights at civil twilight
   twilights = map(twilight.twilight, dates)
   for date in dates:
      twilightTime = twilight.twilight(date)
      opEvents[date].append((twilightTime, "CHECK TOWER LIGHTS: READING ="))

   # random EAS check once per week (taken from last version)
   # EAS tests must be conducted between 8:30 AM and twilight.
   # It is by WMBR convention that they are conducted at half
   # past an hour.  To be conservative, I also bring back the
   # late limit to half-past the previous hour from twilight,
   # thus avoiding any issues involving having the EAS test
   # and twilight too close together.
   for date in easDays:
       random_hour = random.randrange(8,twilightTime.hour)*60*60+30*60
       easDateTime = date + datetime.timedelta(0, random_hour)
       print("EAS: %s" % easDateTime)
       opEvents[date].append((easDateTime, "CONDUCT REQUIRED WEEKLY EAS TEST"))

   return opEvents

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
        raise Exception("The programming log date <%s> cannot be used to generate the date range <%s, %s>" % 
			(date,mindate,maxdate))

      if not date in opEvents:
        mindate,maxdate = min(opEvents.keys()),max(opEvents.keys())
        raise Exception("The programming log date <%s> cannot be used to generate the date range <%s, %s>" % 
			(date,mindate,maxdate))

      if show["type"] == "show":
         progEvents[date].append(model.show(
          show["show_name"],
          date+timestrtodelta(show["start_time"]),
          date+timestrtodelta(show["end_time"]),
          show["engineer"],
          show["producers"],
          show["announcers"]))

      elif show["type"] == "signoff":
        opEvents[date].append((date+timestrtodelta(show["time"]), 'TURN OFF TRANSMITTER'))
        progEvents[date].append(model.signoff(date+timestrtodelta(show["time"])))
      elif show["type"] == "signon":
        opEvents[date].append((date+timestrtodelta(show["time"]), 'TEST EAS LIGHTS AND TURN ON TRANSMITTER'))
        progEvents[date].append(model.signon(date+timestrtodelta(show["time"])))

  return progEvents,opEvents

def getSchedule(source,today,numdays):
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

def generateLogs(argv, printcmd, location="."):
  # FIRST, figure out what days we are going to be printing logs for
  
  
  calendar.setfirstweekday(calendar.SUNDAY)
  
  parser = argparse.ArgumentParser(description="loghound: generates program and operating logs")
  parser.add_argument("year", type=int, help="the year of the log to create.") 
  parser.add_argument("month", type=int, help="the month of the log to create.") 
  parser.add_argument("day", type=int, help="the starting day of the log to create.") 
  parser.add_argument("numdays", type=int, default=7,help="the number of days to generate..") 
  parser.add_argument("-a","--alt", action='store_true', help="mark alternate shows")	
  parser.add_argument("-b","--blank", action='store_true', help="insert blank spaces")	
  parser.add_argument("-s","--source",choices=["web-live","local","web-local"], default="web-live", 
		  help="source to get programming guide information from.")
  parser.add_argument("-i","--input", type=str, help="programming guide file (if local source is selected")

 
  args = parser.parse_args()
  today = datetime.datetime(args.year,args.month,args.day)

  if today.weekday() != calendar.SUNDAY:
    printcmd("This is supposed to start on a Sunday.  I assume you know what you're doing.\n")
  
  printcmd("Adding shows...")
  sched_raw = getSchedule(args.source,today,args.numdays)
  progEvents,opEvents = parseSchedule(sched_raw,today,args.numdays)

  if args.alt:
     lastweek = today - datetime.timedelta(days=7)
     last_sched_raw = getSchedule(args.source,lastweek,args.numdays)
     lastProgEvents,lastOpEvents = parseSchedule(last_sched_raw,lastweek,args.numdays)
     progEvents = computeAltShows(lastProgEvents,progEvents)
    
    # THIRD, compute other events that will occur on a particular day

  printcmd("Inserting FCC events (EAS tests, tower lights)...")
  opEvents = insertFCCEvents(opEvents,today,args.numdays)
  # FOURTH, produce the pdf
  generateOpLog(opEvents,today,args.numdays,
          location=location)

  generateProgLog(progEvents,today,args.numdays,
          location=location,
          add_blanks=args.blank)
 ## The programming log
  printcmd("Finished.\n")

if __name__ == '__main__':
  def printcmd(x):
    sys.stderr.write("%s\n" % x)
    sys.stderr.flush()
  generateLogs(sys.argv, printcmd)
