"""
A service implementation should (at minimum) meet the requirements set here. Following
the API below makes it easy to create a Windows service.
"""

from abc import abstractmethod, abstractproperty, ABCMeta


class WindowsServiceMetadata(metaclass=ABCMeta):
   "Required service metadata used by Windows service manager"

   @abstractproperty
   def _svc_name_(self):
      "required from a Python Windows service class"

   @abstractproperty
   def _svc_display_name_(self):
      "required from a Python Windows service class"

   @abstractproperty
   def _svc_description_(self):
      "required from a Python Windows service class"


class WindowsServiceControl(metaclass=ABCMeta):
   "Required methods used by Windows service manager to start & stop the service"

   @abstractmethod
   def SvcDoRun(self):
      "called by Windows service manager to run the service"

   @abstractmethod
   def SvcStop(self):
      "called by Windows service manager to stop the service"


class WindowsServiceABC(WindowsServiceMetadata, WindowsServiceControl):
   "a convenience ABC for service implementations"
