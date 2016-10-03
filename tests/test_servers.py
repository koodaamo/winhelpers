import sys, time
import win32service, win32serviceutil, pywintypes
from winhelpers.service import BaseService, BaseAsyncioService, WAMPComponentService
from pytest import fixture, raises

tested_services = (BaseService, BaseAsyncioService, WAMPComponentService)

@fixture(scope="module", params=tested_services)
def service(request):
   yield request.param
   return

@fixture(scope="module", params=tested_services)
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


def test_01_install_remove(service):
   sys.argv = sys.argv[:1] + ["install"]
   win32serviceutil.HandleCommandLine(service)
   status_code = win32serviceutil.QueryServiceStatus(service._svc_name_)[1]
   assert status_code ==  win32service.SERVICE_STOPPED
   sys.argv = sys.argv[:1] + ["remove"]
   win32serviceutil.HandleCommandLine(service)
   with raises(pywintypes.error):
      status_code = win32serviceutil.QueryServiceStatus(service._svc_name_)[1]

def test_02_start_stop(installed):

   sys.argv = sys.argv[:1] + ["start"]
   win32serviceutil.HandleCommandLine(installed)

   while True:
      status_code = win32serviceutil.QueryServiceStatus(installed._svc_name_)[1]
      if status_code == win32service.SERVICE_RUNNING:
         break

   sys.argv = sys.argv[:1] + ["stop"]
   win32serviceutil.HandleCommandLine(installed)
