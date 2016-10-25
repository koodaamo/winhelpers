import sys
import win32serviceutil
from .service.testing import *


def winhelper():
   if len(sys.argv) < 3:
      print("syntax: winhelper [install/remove/start/stop] [DummyService/DummyAsyncioService/DummyAsyncioTransportService/DummyWAMPService]")
      sys.exit()
   srvklass = sys.argv.pop()
   win32serviceutil.HandleCommandLine(eval(srvklass))
