import sys, logging, re, threading
from logging.handlers import NTEventLogHandler
import win32serviceutil
import win32event
import win32service
import servicemanager

# messages for reporting status to the service manager
from win32service import SERVICE_START_PENDING, \
                         SERVICE_RUNNING, \
                         SERVICE_STOP_PENDING, \
                         SERVICE_STOPPED


from .util import servicemetadataprovider, eventloggerprovider


# Basic dummy service for reference; note that the servicemanager apparently runs the
# service in a separate thread yet calls the functions in main, so don't count on
# execution being intuitive...

@eventloggerprovider
@servicemetadataprovider
class MinimalService(win32serviceutil.ServiceFramework):

   def __init__(self,args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(win32service.SERVICE_START_PENDING, waitHint=60000)
      self.stop_event = win32event.CreateEvent(None, 0, 0, None)

   def SvcStop(self):
      self._logger.info("stopping")
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self.stop_event)

   def SvcDoRun(self):
      self._logger.info("starting")
      self.ReportServiceStatus(win32service.SERVICE_RUNNING)
      win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
      self.ReportServiceStatus(win32service.SERVICE_STOPPED)


# Service base class

class WindowsServiceBase(win32serviceutil.ServiceFramework):

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self._stop_event = win32event.CreateEvent(None, 0, 0, None)

   def start(self):
      servicemanager.LogWarningMsg("the start method should be overriden")
      win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)
      self.stop()

   def stop(self):
      servicemanager.LogWarningMsg("the stop method should be overriden")
      self.ReportServiceStatus(SERVICE_STOPPED)

   def SvcDoRun(self):
      "service controller is telling us to start"
      self.ReportServiceStatus(SERVICE_START_PENDING, waitHint=60000)
      self.ReportServiceStatus(SERVICE_RUNNING)
      self.start()

   def SvcStop(self):
      "the service controller is telling us to shut down"
      self.ReportServiceStatus(SERVICE_STOP_PENDING)
      win32event.SetEvent(self._stop_event)



