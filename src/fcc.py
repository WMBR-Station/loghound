#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import random
import twilight
import calendar
import numpy as np


def insertEASTimes(dates,opEvents):
  
   # random EAS check once per week (taken from last version)
   # EAS tests must be conducted between 8:30 AM and twilight.
   # It is by WMBR convention that they are conducted at half
   # past an hour.  To be conservative, I also bring back the
   # late limit to half-past the previous hour from twilight,
   # thus avoiding any issues involving having the EAS test
   # and twilight too close together.
   def get_week(date):
     weeks = np.array(calendar.monthcalendar(date.year,date.month))
     week = np.where(weeks==date.day)[0][0] + 1
     return week

   def random_time(day):
     twilight_hour = twilight.twilight(day).hour
     random_hour = random.randrange(8,twilight_hour)
     easDateTime = date + datetime.timedelta(hours=random_hour,minutes=30)
     return easDateTime

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

   for date in easDays:
       easDateTime = random_time(date)
       print("EAS: %s" % easDateTime)
       opEvents[date].append((easDateTime, "CONDUCT REQUIRED WEEKLY EAS TEST"))

   return opEvents

def insertTowerCheckTimes(dates,opEvents):
   # check the tower lights at civil twilight
   twilights = map(twilight.twilight, dates)
   for date in dates:
      twilightTime = twilight.twilight(date)
      opEvents[date].append((twilightTime, "CHECK TOWER LIGHTS: READING ="))

def insertFCCEvents(printcmd,opEvents,today,numdays):
   dates = [today + datetime.timedelta(i) for i in xrange(numdays)]
   # which dates should have an EAS test?
   insertTowerCheckTimes(dates,opEvents)
   insertEASTimes(dates,opEvents)
   return opEvents

