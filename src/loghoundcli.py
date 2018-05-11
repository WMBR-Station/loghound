#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse

import os
import sys
import calendar
import datetime

import getlog
import genlog
import fcc
import model

def computeAltShows(lastProgLog,currProgLog):
  alternating = {}
  currShows = []
  lastShows = []

  for day in currProgLog:
     get_names = lambda data: map(lambda x : x.name, 
              filter(lambda x : isinstance(x,model.show),data))
     lastday = day - datetime.timedelta(days=7)

     currShows += get_names(currProgLog[day])
     lastShows += get_names(lastProgLog[lastday])

  alternating = list(set(currShows).difference(set(lastShows)))

  for day in currProgLog:
     for show in currProgLog[day]:
        if isinstance(show,model.show) and show.name in alternating:
           show.alternates(True)

  return currProgLog

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
  progEvents,opEvents = getlog.load(printcmd,args.source,today,args.numdays)

  if args.alt:
     lastweek = today - datetime.timedelta(days=7)
     lastProgEvents,_= getlog.load(printcmd,args.source,lastweek,args.numdays)
     progEvents = computeAltShows(lastProgEvents,progEvents)

    # THIRD, compute other events that will occur on a particular day

  printcmd("Inserting FCC events (EAS tests, tower lights)...")
  opEvents = fcc.insertFCCEvents(printcmd,opEvents,today,args.numdays)
  # FOURTH, produce the pdf
  genlog.generateOpLog(printcmd,opEvents,today,args.numdays,
          location=location)

  genlog.generateProgLog(printcmd,progEvents,today,args.numdays,
          location=location,
          add_blanks=args.blank)
  ## The programming log
  printcmd("Finished.\n")

if __name__ == '__main__':
  def printcmd(x):
    sys.stderr.write("%s\n" % x)
    sys.stderr.flush()
  generateLogs(sys.argv, printcmd)
