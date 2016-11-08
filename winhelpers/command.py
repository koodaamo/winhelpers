import sys
import win32serviceutil
from .service.windows import MinimalReferenceService
from .service.examples.windows import WindowsAsyncioService, WindowsWAMPService


def winhelper():
   if len(sys.argv) < 3:
      print("syntax: winhelper [install/remove/start/stop] [MinimalReferenceService/WindowsAsyncioService/WindowsWAMPService]")
      sys.exit()
   srvklass = sys.argv.pop()
   win32serviceutil.HandleCommandLine(eval(srvklass))
