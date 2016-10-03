import sys
import win32serviceutil
from .service import BaseService, BaseAsyncioService, WAMPComponentService


def winhelper():
   if len(sys.argv) < 3:
      print("syntax: service [install/remove/start/stop] [BaseService/BaseAsyncioService/WAMPComponentService]")
      sys.exit()
   srvklass = sys.argv.pop()
   win32serviceutil.HandleCommandLine(eval(srvklass))
