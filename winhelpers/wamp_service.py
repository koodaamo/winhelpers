import asyncio

import win32serviceutil
import win32service
import win32event
import win32api
import win32timezone
import servicemanager
import win32traceutil

import txaio
from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
from autobahn.asyncio.websocket import WampWebSocketClientFactory

from .registry import get_setting

def logevent(msg, evtid=0xF000):
   "log into windows event manager"
   servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, evtid, (msg, ''))


class WAMPService(win32serviceutil.ServiceFramework):

   _svc_name_ = "WAMPService"
   _svc_display_name_ = "WAMP Service"
   _svc_description_ = "Windows service for running a WAMP component"

   wmp_url = None
   wmp_realm = None
   wmp_extra = None
   wmp_sessioncomponent = None
   wmp_serializers = None
   wmp_ssl = None


   def __init__(self,args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.wmp_url = self.wmp_url or get_setting("router_url")
      self.wmp_realm = self.wmp_realm or get_setting("router_realm")
      self.ReportServiceStatus(win32service.SERVICE_START_PENDING, waitHint=60000)
      logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTING)
      self.stop_event = win32event.CreateEvent(None, 0, 0, None)

   def _do_ssl(self, isSecureURL):
      if self.wmp_ssl is None:
         return isSecureURL
      else:
         if self.wmp_ssl and not isSecureURL:
             raise RuntimeError(
                 'ssl argument value defined in %s conflicts with the "ws:" '
                 'prefix of the url argument. Did you mean to use "wss:"?' %
                 self.__class__.__name__)
         return self.wmp_ssl

   def _component(self):
      "application session (component) factory"

      cfg = ComponentConfig(self.wmp_realm, self.wmp_extra)
      try:
         session = self.wmp_sessioncomponent(cfg)
      except Exception:
         #self.log.failure("App session could not be created! ")
         self.loop.stop()
      else:
         return session

   def _waiter(self):
      "win32 stop event waiter factory"

      win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
      self.loop.stop()
      if self._protocol._session:
         loop.run_until_complete(self._protocol._session.leave())
      self.ReportServiceStatus(win32service.SERVICE_STOPPED)
      self.loop.close()

   def SvcStop(self):
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self.stop_event)

   def SvcDoRun(self):
      txaio.use_asyncio()
      self.loop = txaio.config.loop = loop = asyncio.get_event_loop()
      isSecureURL, host, port, resource, path, params = parse_url(self.wmp_url)
      make_transport = WampWebSocketClientFactory(self._component,
                                                  url=self.wmp_url,
                                                  serializers=self.wmp_serializers)
      ssl = self._do_ssl(isSecureURL)
      transport_coro = self.loop.create_connection(make_transport, host, port, ssl=ssl)
      (transport, self._protocol) = loop.run_until_complete(transport_coro)

      stop_waiter_coro = loop.run_in_executor(None, self._waiter)
      loop.run_until_complete(stop_waiter_coro)

      self.ReportServiceStatus(win32service.SERVICE_RUNNING)
      logevent(self._svc_display_name_, servicemanager.PYS_SERVICE_STARTED)

      loop.run_forever()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SideKickService)
