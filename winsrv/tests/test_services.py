import sys, time, logging, functools
from logging.handlers import NTEventLogHandler

from pytest import raises, mark, fail
import win32service, win32serviceutil, pywintypes

from win32service import SERVICE_RUNNING, SERVICE_START_PENDING, SERVICE_STOPPED
from win32serviceutil import QueryServiceStatus

from ..service import WindowsServiceBase, ServiceControls
from ..util import log_exception, servicemetadataprovider, eventloggerprovider
from ..abcs import WindowsServiceABC
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
class BasicWindowsService(WindowsServiceBase, ServiceControls):
   "test service that is capable of being managed but does nothing else"


tested_services = (BasicWindowsService,)


@mark.parametrize('service', tested_services)
def test_01_install_remove(service):

   service.install_service()

   # check that service is installed
   assert QueryServiceStatus(service._svc_name_)[1] == SERVICE_STOPPED

   service.remove_service()

   # check that service is not installed any more
   with raises(pywintypes.error):
      status = QueryServiceStatus(service._svc_name_)


@mark.parametrize("service", tested_services)
def test_02_start_stop(installed):

   assert QueryServiceStatus(installed._svc_name_)[1] == SERVICE_STOPPED

   installed.start_service(wait=3)
   assert QueryServiceStatus(installed._svc_name_)[1] == SERVICE_RUNNING

   installed.stop_service(wait=3)
   assert QueryServiceStatus(installed._svc_name_)[1] == SERVICE_STOPPED
