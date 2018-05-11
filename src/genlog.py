#!/usr/bin/python
# -*- coding: utf-8 -*-
from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate, Table, TableStyle, Paragraph, flowables
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
import datetime

import tablegen
import progtablegen

def generateLog(printcmd,logEvents,today,numdays,location='.',oplog=True,add_blanks=False):
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

  printcmd(">> Building PDF File of Log <<")

  if oplog:
	  printcmd("Writing operating log...")
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


def generateProgLog(printcmd,progEvents,today,numdays,location='.',add_blanks=False):
   generateLog(printcmd,progEvents,today,numdays,location='.',
               oplog=False,add_blanks=add_blanks)

def generateOpLog(printcmd,opEvents,today,numdays,location='.'):
   generateLog(printcmd,opEvents,today,numdays,location='.',
               oplog=True)

