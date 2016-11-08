import sys, logging, re
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

from .abcs import WindowsServiceMetadata, ControlledService


# Windows logger factory

def get_windows_logger(name="Python Windows service", level=logging.INFO):
   logger = logging.getLogger(name)
   logger.setLevel(level)
   logger.addHandler(NTEventLogHandler(name))
   return logger


# Windows servicemanager eats exceptions, so need some extra logging magic...

exception_logger = get_windows_logger(name="Python exceptions", level=logging.DEBUG)

def log_exception(exctype, value, tb):
   exception_logger.error("%s (%s): %s" % (exctype, value, tb))

sys.excepthook = log_exception


# Utilities for service creation

def set_logger(name, dct):
   dct["logger"] = get_windows_logger(name=name)
   return dct

def ccc(name): # Camel Case Converter
   s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
   return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)

def set_service_metadata(name, dct):
   dct["_svc_name_"] = name
   nname = ccc(name) # normalized
   dct["_svc_display_name_"] = nname + " service base"
   dct["_svc_description_"] =   "A subclassable " + nname + " service base"
   return dct


# For reference; note that the servicemanager apparently runs the service in a separate
# thread yet calls the functions in main, so don't count on sane execution...

class MinimalReferenceService(win32serviceutil.ServiceFramework):
   "Raw minimum standalone dummy service example, for reference and comparison"

   _svc_name_ = "MinimalReferenceService"
   _svc_display_name_ = "Minimal reference service"
   _svc_description_ = "This is a minimal windows reference service."

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(SERVICE_START_PENDING, waitHint=60000)
      #logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTING)
      self._stop_event = win32event.CreateEvent(None, 0, 0, None)
      servicemanager.LogInfoMsg("initialized %s" % self._svc_name_)


   def SvcStop(self):
      servicemanager.LogInfoMsg("stop requested of %s" % self._svc_name_)
      self.ReportServiceStatus(SERVICE_STOP_PENDING)
      win32event.SetEvent(self._stop_event)

   def SvcDoRun(self):
      #logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTED)
      servicemanager.LogInfoMsg("running %s" % self._svc_name_)
      self.ReportServiceStatus(SERVICE_RUNNING)
      servicemanager.LogInfoMsg("now starting to wait in %s" % self._svc_name_)
      win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)
      self.ReportServiceStatus(SERVICE_STOPPED)
      servicemanager.LogInfoMsg("%s stopped" % self._svc_name_)


# Service base class

class WindowsServiceBase(win32serviceutil.ServiceFramework):

   def __init__(self, *args):
      win32serviceutil.ServiceFramework.__init__(self, *args)
      self._stop_event = win32event.CreateEvent(None, 0, 0, None)

   def SvcDoRun(self):
      "service controller is telling us to start"
      self.ReportServiceStatus(SERVICE_START_PENDING, waitHint=60000)
      self.ReportServiceStatus(SERVICE_RUNNING)
      self._start_waiter()
      self.start()
      return

   def _start_waiter(self):
      "listen for service end request, blocking until receiving request, then call stop"
      win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)

   def SvcStop(self):
      "the service controller is telling us to shut down"
      self.ReportServiceStatus(SERVICE_STOP_PENDING)
      win32event.SetEvent(self._stop_event)
      self.ReportServiceStatus(SERVICE_STOPPED)


# Creator metaclass

class WindowsServiceCreator(type):

   def configure_service_class(cls, name, parents, dct):
      parents = list(parents)
      #parents.append(WindowsServiceBase)
      dct = set_service_metadata(name, dct)
      dct = set_logger(name, dct)
      return (cls, name, tuple(parents), dct)

   def __new__(*args):
      args  = WindowsServiceCreator.configure_service_class(*args)
      return type.__new__(*args)


