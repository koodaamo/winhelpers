import sys, time, logging, functools
from logging.handlers import NTEventLogHandler

from pytest import raises, fixture
import win32service, win32serviceutil, servicemanager, pywintypes

from asynciohelpers.abcs import ServiceBaseABC, WAMPServiceABC
from asynciohelpers.util import provides_abc
from asynciohelpers.testing import NotImplementedABC

from ..abcs import WindowsServiceMetadata, ControlledWindowsService
from ..service import WindowsServiceBase
from ..util import log_exception
from .services import BasicWindowsService, BasicWindowsAsyncioService, \
                      ConnectingWindowsAsyncioService, ReConnectingWindowsAsyncioService, \
                      WindowsWAMPService, EnvConfiguredReConnectingWindowsAsyncioService

logging.basicConfig()

tested_services = (BasicWindowsService, BasicWindowsAsyncioService, \
                   ConnectingWindowsAsyncioService, ReConnectingWindowsAsyncioService, \
                   WindowsWAMPService,)

event_logger = logging.getLogger("PythonService")
event_logger.setLevel(logging.DEBUG)
event_logger.addHandler(NTEventLogHandler("PythonService"))
sys.excepthook = functools.partial(log_exception, event_logger)


@fixture(scope="module", params=tested_services)
def servicefactory(request):
   klass = request.param
   bases = list(klass.__bases__)
   if WindowsServiceBase not in bases:
      bases.insert(0, WindowsServiceBase)
      klass.__bases__ = tuple(bases)
   yield klass
   return


@fixture(scope="function", params=tested_services)
def installed(request):
   srv_klass = request.param
   sys.argv = sys.argv[:1] + ["install"]
   win32serviceutil.HandleCommandLine(srv_klass)
   while True:
      try:
         status_code = win32serviceutil.QueryServiceStatus(srv_klass._svc_name_)[1]
         break
      except:
         pass
   yield srv_klass
   while True:
      status_code = win32serviceutil.QueryServiceStatus(srv_klass._svc_name_)[1]
      if status_code == win32service.SERVICE_STOPPED:
         break
   sys.argv = sys.argv[:1] + ["remove"]
   win32serviceutil.HandleCommandLine(srv_klass)


def test_00_validate(servicefactory):
   assert provides_abc(servicefactory, WindowsServiceMetadata)
   assert provides_abc(servicefactory, ControlledWindowsService)
   assert not provides_abc(servicefactory, NotImplementedABC)

   if servicefactory in (ConnectingWindowsAsyncioService, ReConnectingWindowsAsyncioService, WindowsWAMPService):
      assert provides_abc(servicefactory, ServiceBaseABC)

   if servicefactory == WindowsWAMPService:
      assert provides_abc(servicefactory, WAMPServiceABC)


def test_01_install_remove(servicefactory):
   sys.argv = sys.argv[:1] + ["install"]
   win32serviceutil.HandleCommandLine(servicefactory)
   status_code = win32serviceutil.QueryServiceStatus(servicefactory._svc_name_)[1]
   assert status_code ==  win32service.SERVICE_STOPPED
   sys.argv = sys.argv[:1] + ["remove"]
   win32serviceutil.HandleCommandLine(servicefactory)
   with raises(pywintypes.error):
      status_code = win32serviceutil.QueryServiceStatus(servicefactory._svc_name_)[1]


def test_02_start_stop(installed):
   sys.argv = sys.argv[:1] + ["start"]
   servicemanager.LogInfoMsg("trying to start %s" % str(installed))
   win32serviceutil.HandleCommandLine(installed)

   pending_stat = win32serviceutil.QueryServiceStatus(installed._svc_name_)[1]
   assert pending_stat == win32service.SERVICE_START_PENDING

   while True:
      status_code = win32serviceutil.QueryServiceStatus(installed._svc_name_)[1]
      if status_code == win32service.SERVICE_RUNNING:
         time.sleep(3)
         break
      assert status_code != win32service.SERVICE_STOPPED, "service did not start"

   sys.argv = sys.argv[:1] + ["stop"]
   win32serviceutil.HandleCommandLine(installed)


