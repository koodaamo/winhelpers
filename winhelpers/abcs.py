from abc import abstractmethod, abstractproperty, ABCMeta


class WindowsServiceMetadata(metaclass=ABCMeta):
   "Windows service metadata"

   @abstractproperty
   def _svc_name_(self):
      "required from a Python Windows service class"

   @abstractproperty
   def _svc_display_name_(self):
      "required from a Python Windows service class"

   @abstractproperty
   def _svc_description_(self):
      "required from a Python Windows service class"


class ControlledService(metaclass=ABCMeta):
   "Windows service control API"

   @abstractmethod
   def SvcDoRun(self):
      "called by Windows service manager to run the service"

   @abstractmethod
   def SvcStop(self):
      "called by Windows service manager to stop the service"


