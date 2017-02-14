import win32serviceutil
import win32event
import win32service
import servicemanager
import winerror

from win32service import SERVICE_START_PENDING, \
                         SERVICE_RUNNING, \
                         SERVICE_STOP_PENDING, \
                         SERVICE_STOPPED

from win32serviceutil import ServiceFramework, StartService, StopService, WaitForServiceStatus, \
                             StopServiceWithDeps, GetServiceClassString, \
                             RemoveService, InstallService

from .util import servicemetadataprovider, eventloggerprovider


# Service base class; note that the subclass needs to provide the service metadata

class WindowsServiceBase(ServiceFramework):
   "base class for implementing Windows services using pywin32"

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self._stop_event = win32event.CreateEvent(None, 0, 0, None)
      self.ReportServiceStatus(SERVICE_START_PENDING, waitHint=60000)

   def start(self):
      servicemanager.LogWarningMsg("the start method should be overriden")
      win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)
      self.stop()

   def stop(self):
      servicemanager.LogWarningMsg("the stop method should be overriden")
      self.ReportServiceStatus(SERVICE_STOPPED)

   def SvcDoRun(self):
      "service controller is telling us to start"
      self.start()

   def SvcStop(self):
      "the service controller is telling us to shut down"
      self.ReportServiceStatus(SERVICE_STOP_PENDING)
      win32event.SetEvent(self._stop_event)


# Service controls support mixin class

class ServiceControls:
   "implement service install/remove and start/stop"

   @classmethod
   def install_service(klass):
      # Much simplified install; see pywin32 win32serviceutil sources for full details
      try:
         InstallService(
            GetServiceClassString(klass),
            klass._svc_name_,
            klass._svc_display_name_)
      except win32service.error as exc:
         if exc.winerror == winerror.ERROR_SERVICE_EXISTS:
            klass._logger.error("Not installing (already installed)")
         else:
            klass._logger.error("Cannot install: %s (%d)" % (exc.strerror, exc.winerror))

   @classmethod
   def remove_service(klass):
      try:
         RemoveService(klass._svc_name_)
      except win32service.error as exc:
         klass._logger.error("Cannot remove: %s (%d)" % (exc.strerror, exc.winerror))

   @classmethod
   def start_service(klass, wait=0):
      try:
         StartService(klass._svc_name_)
         if wait:
            WaitForServiceStatus(klass._svc_name_, SERVICE_RUNNING, wait)
      except win32service.error as exc:
         klass._logger.error("Cannot start: %s" % exc.strerror)

   @classmethod
   def stop_service(klass, wait=0):
      try:
         if wait:
            StopServiceWithDeps(klass._svc_name_, waitSecs=wait)
         else:
            StopService(klass._svc_name_)
      except win32service.error as exc:
         klass._logger.error("Service stop error: %s (%d)" % (exc.strerror, exc.winerror))





