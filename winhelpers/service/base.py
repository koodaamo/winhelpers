import win32service
import win32serviceutil
import win32event
import servicemanager
from servicemanager import LogMsg, LogErrorMsg, LogInfoMsg, LogWarningMsg


class BaseService(win32serviceutil.ServiceFramework):

   _svc_name_ = "BaseService"
   _svc_display_name_ = "Base service helper"
   _svc_description_ = "A subclassable service base class"

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(win32service.SERVICE_START_PENDING, waitHint=60000)
      self.log_evt(servicemanager.PYS_SERVICE_STARTING)
      self._stop_event = win32event.CreateEvent(None, 0, 0, None)


   def log_evt(self, evtid):
      "convenience for logging the service lifecycle events"
      LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, evtid, (self._svc_display_name_, ''))


   def main(self):
      "dummy main that just waits for the stop event"
      win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)

   def SvcDoRun(self):
      "service controller is telling us to start; let's comply"

      LogInfoMsg("%s service start requested" % self._svc_name_)

      # log start to event log and report to service controller
      self.log_evt(servicemanager.PYS_SERVICE_STARTED)
      self.ReportServiceStatus(win32service.SERVICE_RUNNING)

      # let the main app do its job; it has to block and return cleanly at exit
      self.main()

      # log stop to event log and report to service controller
      self.log_evt(servicemanager.PYS_SERVICE_STOPPED)
      self.ReportServiceStatus(win32service.SERVICE_STOPPED)
      return


   def SvcStop(self):
      "the service controller is shutting us down, so trigger the stop event"
      LogInfoMsg("%s: service stop called" % self._svc_name_)
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self._stop_event)

