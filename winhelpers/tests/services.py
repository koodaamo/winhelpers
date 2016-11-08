"""
 Example services
"""

import os, asyncio

import win32service
import win32serviceutil
import win32event
import servicemanager

from autobahn.asyncio.wamp import ApplicationSession

from asynciohelpers.service import AsyncioServiceBase
from asynciohelpers.service import AsyncioReConnectingServiceBase
from asynciohelpers.wamp import WAMPServiceMixin, WAMPConfigAdapter

from winhelpers.abcs import WindowsServiceMetadata, ControlledService
from winhelpers.service import WindowsServiceBase, WindowsServiceCreator, get_windows_logger, WindowsMetadataAdapter


def logevent(msg, evtid=0xF000):
   "log into windows event manager"
   servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, evtid, (msg, ''))


# Basic dummy service for reference; note that the servicemanager apparently runs the
# service in a separate thread yet calls the functions in main, so don't count on
# execution being intuitive...

class Service(win32serviceutil.ServiceFramework):

   _svc_name_ = "TestService"
   _svc_display_name_ = "Test Service"
   _svc_description_ = "This is a bare-bones windows service for testing."

   def __init__(self,args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(win32service.SERVICE_START_PENDING, waitHint=60000)
      logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTING)
      self.stop_event = win32event.CreateEvent(None, 0, 0, None)

   def SvcStop(self):
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self.stop_event)

   def SvcDoRun(self):
      logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTED)
      self.ReportServiceStatus(win32service.SERVICE_RUNNING)
      win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
      self.ReportServiceStatus(win32service.SERVICE_STOPPED)



class MinimalReferenceService(win32serviceutil.ServiceFramework):
   "Raw minimum standalone dummy service example, for reference and comparison"

   _svc_name_ = "MinimalReferenceService"
   _svc_display_name_ = "Minimal reference service"
   _svc_description_ = "This is a minimal windows reference service."

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(SERVICE_START_PENDING, waitHint=60000)
      #logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTING)
      self._stop_event = win32event.CreateEvent(None, 0, 0, None)
      servicemanager.LogInfoMsg("initialized %s" % self._svc_name_)


   def SvcStop(self):
      servicemanager.LogInfoMsg("stop requested of %s" % self._svc_name_)
      self.ReportServiceStatus(SERVICE_STOP_PENDING)
      win32event.SetEvent(self._stop_event)

   def SvcDoRun(self):
      #logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTED)
      servicemanager.LogInfoMsg("running %s" % self._svc_name_)
      self.ReportServiceStatus(SERVICE_RUNNING)
      servicemanager.LogInfoMsg("now starting to wait in %s" % self._svc_name_)
      win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)
      self.ReportServiceStatus(SERVICE_STOPPED)
      servicemanager.LogInfoMsg("%s stopped" % self._svc_name_)


#
# Asyncio examples
#


class BasicWindowsAsyncioService(WindowsServiceBase, AsyncioServiceBase, metaclass=WindowsServiceCreator):
   "service that does basically nothing but runs the loop"

   #_svc_name_ = "BasicAsyncioService"
   #_svc_display_name_ = "Basic Asyncio service"
   #_svc_description_ = "This is a Basic Asyncio service."


class TransportProtocol(asyncio.Protocol):

   @property
   def logger(self):
      try:
         return self._logger
      except:
         self._logger = get_windows_logger(name=self.__class__.__name__)
         return self._logger

   def connection_made(self, transport):
      self.logger.debug("connection made")

   def connection_lost(self, exc):
      self.logger.debug("connection lost")



class ReConnectingWindowsAsyncioService(WindowsServiceBase, AsyncioReConnectingServiceBase, metaclass=WindowsServiceCreator):
   "service that connects a transport, reconnecting as necessary"

   _transport_factory = TransportProtocol


class WindowsAsyncioService(WindowsServiceBase, AsyncioReConnectingServiceBase, metaclass=WindowsServiceCreator):
   """
   def _transport_connector(self):
      "return the transport connector coroutine"
      HOST = os.environ.get("TEST_HOST")
      PORT = os.environ.get("TEST_PORT")
      assert (HOST and PORT), "TEST_HOST or TEST_PORT variable not in environment: %s" % ', '.join(os.environ.keys())
      connector = self._loop.create_connection(DummyTransportProtocol, host=HOST, port=PORT)
      self.logger.debug("created transport connector: %s" %  str(connector))
      return connector
   """


#
# WAMP example services
#

class WAMPComponent(ApplicationSession):
   ""

   @property
   def logger(self):
      try:
         return self._logger
      except:
         self._logger = get_windows_logger(name=self.__class__.__name__)
         return self._logger

   def onJoin(self, details):
      self.logger.debug("joined realm")


class WindowsWAMPService(WindowsServiceBase, WAMPServiceMixin, WAMPConfigAdapter, WindowsMetadataAdapter):

   @property
   def wmp_url(self):
      url = os.environ.get("WAMP_ROUTER_URL")
      self.logger.debug("using ws URL '%s'" % url)
      return url

   wmp_realm = "realm1"
   wmp_sessioncomponent = WAMPComponent
