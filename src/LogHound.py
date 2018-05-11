#!/usr/bin/env python
try:
    import tkinter as tk
    import tkinter.filedialog as tk_filedialog
except:
    import Tkinter as tk
    from Tkinter import TclError as tk_error
    import tkFileDialog as tk_filedialog

from TkCalendar import TkCalendar
from loghoundcli import *
from time import localtime
import threading

class LogHound(tk.Frame):
  def __init__(self,parent):
    tk.Frame.__init__(self,parent)
    year,month,day = localtime()[0:3]
    self.calendar = TkCalendar(self,year,month,day)
    self.calendar.pack()
    f = tk.Frame(self)
    f.pack(fill=tk.Y)
    self.genButton = tk.Button(self,
        text='generate',
	command=self.generate,
        relief=tk.FLAT)
    self.genButton.pack()
    self.log = tk.Text(self, width=80, height=10, background="grey")
    self.log.pack(side="left", expand="yes", fill="both")
    self.log.insert('end', 'LogHound ready\n')
    self.log['state'] = 'disabled'

    self.logbar = tk.Scrollbar(self)
    self.logbar.pack(side="right", fill="y")
    self.log['yscrollcommand'] = self.logbar.set
    self.logbar['command'] = self.log.yview

  def printcmd(self,x):
    self.log['state'] = 'normal'
    self.log.insert('end', "%s\n" % x)
    self.log['state'] = 'disabled'
    self.log.yview(tk.MOVETO, 1)
    print("[LOG]: %s" % x)

  def generate(self):
    if self.calendar.chosenrow is None:
      self.printcmd("Please select a week.")
      return
    dirname = tk_filedialog.askdirectory(parent=self, initialdir="/",
                                         title="Please select a directory to write to")
    if len(dirname.strip()) == 0:
      self.printcmd("Please select a directory to write the log to!")
      return
    self.printcmd("Writing to %s" % dirname)
    y,m,d = self.calendar.chosenDay()
    self.printcmd("*"*23 + " log for week starting %4d/%02d/%02d " % (y,m,d) + "*"*23)
    self.genButton['state'] = 'disabled'

    def subgen():
      try:

          argv = ["%d" % y,
                  "%d" % m,
                  "%d" % d,
                  "%d" % 7,
                  '--alt','--blank','--source',"web-live"]

          generateLogs(argv, self.printcmd, dirname)

      except Exception as e:
        self.printcmd("\n>>>> ERROR: \n " + str(e) + "\n")

      self.genButton['state'] = 'normal'
    genThread = threading.Thread(target=subgen)
    genThread.start()

if __name__ == '__main__':
  root = tk.Tk()
  root.title("LogHound")
  c = LogHound(root)
  c.pack()
  try: 
      root.tk.call('console', 'hide')
  except tk_error:
      # Some versions of the Tk framework don't have a console object 
      pass 
  root.mainloop()
