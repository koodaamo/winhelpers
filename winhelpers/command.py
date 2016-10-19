import sys
import win32serviceutil
from .service import BaseService, BaseAsyncioService, DummyWAMPService


def winhelper():
   if len(sys.argv) < 3:
      print("syntax: winhelper [install/remove/start/stop] [BaseService/BaseAsyncioService/DummyWAMPService]")
      sys.exit()
   srvklass = sys.argv.pop()
   win32serviceutil.HandleCommandLine(eval(srvklass))
