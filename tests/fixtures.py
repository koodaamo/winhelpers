import sys
import win32serviceutil, win32service
from pytest import fixture

from . import tested_services


@fixture(scope="module", params=tested_services)
def service(request):
   yield request.param
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
