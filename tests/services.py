import win32service
import win32serviceutil
import win32event
import servicemanager


def logevent(msg, evtid=0xF000):
   "log into windows event manager"
   servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, evtid, (msg, ''))


class Service(win32serviceutil.ServiceFramework):

   _svc_name_ = "TestService"
   _svc_display_name_ = "Test Service"
   _svc_description_ = "This is a bare-bones windows service for testing."

   def __init__(self,args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(win32service.SERVICE_START_PENDING, waitHint=60000)
      logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTING)
      self.stop_event = win32event.CreateEvent(None, 0, 0, None)

   def SvcStop(self):
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self.stop_event)

   def SvcDoRun(self):
      logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTED)
      self.ReportServiceStatus(win32service.SERVICE_RUNNING)
      win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
      self.ReportServiceStatus(win32service.SERVICE_STOPPED)
