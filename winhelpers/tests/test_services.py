import sys, time, logging, functools
from logging.handlers import NTEventLogHandler

from pytest import raises, mark
import win32service, win32serviceutil, pywintypes

from ..service import WindowsServiceBase
from ..util import log_exception, servicemetadataprovider, eventloggerprovider

from .fixtures import installed

logging.basicConfig()
event_logger = logging.getLogger("PythonService")
event_logger.setLevel(logging.DEBUG)
event_logger.addHandler(NTEventLogHandler("PythonService"))
sys.excepthook = functools.partial(log_exception, event_logger)

#
# Define a dummy service to test
#

@eventloggerprovider
@servicemetadataprovider
class BasicWindowsService(WindowsServiceBase):
   "service that does basically nothing"


tested_services = (BasicWindowsService,)


@mark.parametrize('serviceklass', tested_services)
def test_01_install_remove(serviceklass):
   sys.argv = sys.argv[:1] + ["install"]
   win32serviceutil.HandleCommandLine(serviceklass)
   status_code = win32serviceutil.QueryServiceStatus(serviceklass._svc_name_)[1]
   assert status_code ==  win32service.SERVICE_STOPPED
   sys.argv = sys.argv[:1] + ["remove"]
   win32serviceutil.HandleCommandLine(serviceklass)
   with raises(pywintypes.error):
      status_code = win32serviceutil.QueryServiceStatus(serviceklass._svc_name_)[1]


@mark.parametrize("srv_klass", tested_services)
def test_02_start_stop(installed):

   status_code = win32serviceutil.QueryServiceStatus(installed._svc_name_)[1]
   assert status_code ==  win32service.SERVICE_STOPPED
   sys.argv = sys.argv[:1] + ["start"]
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
