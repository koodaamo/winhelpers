import sys
from pytest import fixture
import win32service, win32serviceutil


@fixture
def installed(srv_klass):
   "Provide instllation and removal of Windows Service class"

   # install
   sys.argv = sys.argv[:1] + ["install"]
   win32serviceutil.HandleCommandLine(srv_klass)

   # wait for install to complete
   while True:
      try:
         status_code = win32serviceutil.QueryServiceStatus(srv_klass._svc_name_)[1]
         break
      except Exception as exc:
         pass

   # return the installed class
   yield srv_klass

   # wait for the service to stop
   while True:
      status_code = win32serviceutil.QueryServiceStatus(srv_klass._svc_name_)[1]
      if status_code == win32service.SERVICE_STOPPED:
         break

   # remove the service
   sys.argv = sys.argv[:1] + ["remove"]
   win32serviceutil.HandleCommandLine(srv_klass)
