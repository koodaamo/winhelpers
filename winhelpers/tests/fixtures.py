from pytest import raises, fixture
import win32service, win32serviceutil


@fixture(scope="function")
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
