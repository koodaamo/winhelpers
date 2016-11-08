import sys, time, asyncio, logging, signal, multiprocessing, inspect
from pytest import raises, mark

import win32service, win32serviceutil, servicemanager, pywintypes

from .fixtures import service, installed


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
   servicemanager.LogInfoMsg("trying to start %s" % str(installed))
   win32serviceutil.HandleCommandLine(installed)

   pending_stat = win32serviceutil.QueryServiceStatus(installed._svc_name_)[1]
   assert pending_stat == win32service.SERVICE_START_PENDING

   while True:
      status_code = win32serviceutil.QueryServiceStatus(installed._svc_name_)[1]
      if status_code == win32service.SERVICE_RUNNING:
         break
      assert status_code != win32service.SERVICE_STOPPED, "service did not start"

   sys.argv = sys.argv[:1] + ["stop"]
   win32serviceutil.HandleCommandLine(installed)

