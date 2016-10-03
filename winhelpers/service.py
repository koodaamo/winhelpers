import sys, asyncio

import win32service
import win32serviceutil
import win32event
import servicemanager

import txaio
from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
from autobahn.asyncio.websocket import WampWebSocketClientFactory


class BaseService(win32serviceutil.ServiceFramework):

   _svc_name_ = "BaseService"
   _svc_display_name_ = "Helper service base"
   _svc_description_ = "A subclassable service base class"

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(win32service.SERVICE_START_PENDING, waitHint=60000)
      self.log_lifecycle_event(servicemanager.PYS_SERVICE_STARTING)
      self._srv_stop_event = win32event.CreateEvent(None, 0, 0, None)

   def log_lifecycle_event(self, evtid):
      "convenience for logging the service lifecycle events"
      servicemanager.LogMsg(
         servicemanager.EVENTLOG_INFORMATION_TYPE, evtid, (self._svc_display_name_, '')
      )

   def main(self, *args, **kwargs):
      "dummy main that just waits for the stop event"
      win32event.WaitForSingleObject(self._srv_stop_event, win32event.INFINITE)

   def SvcDoRun(self):
      "service controller is telling us to start; let's comply"

      # log start to event log and report to service controller
      self.log_lifecycle_event(servicemanager.PYS_SERVICE_STARTED)
      self.ReportServiceStatus(win32service.SERVICE_RUNNING)

      # let the main app do its job; it has to block and return cleanly at exit
      self.main()

      # log stop to event log and report to service controller
      self.ReportServiceStatus(win32service.SERVICE_STOPPED)
      self.log_lifecycle_event(servicemanager.PYS_SERVICE_STOPPED)


   def SvcStop(self):
      "the service controller is shutting us down, so trigger the stop event"
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self._srv_stop_event)


class BaseAsyncioService(BaseService):
   "base windows service that handles loop management etc."

   _svc_name_ = "AsyncioHelper"
   _svc_display_name_ = "Helper asyncio service base"
   _svc_description_ = "A subclassable service for running an asyncio loop"


   def _stop_event_waiter(self):
      "blocking win32 stop event waiter run in a separate thread"
      win32event.WaitForSingleObject(self._srv_stop_event, win32event.INFINITE)
      try:
         self.loop.stop()
      except:
         pass

   def main(self):
      "loop until interrupted"
      self.loop = loop = asyncio.get_event_loop()
      stop_waiter_coro = loop.run_in_executor(None, self._stop_event_waiter)
      loop.run_until_complete(stop_waiter_coro)
      self.setup_asyncio_app()
      loop.run_forever()
      self.teardown_asyncio_app()
      loop.close()

   def setup_asyncio_app(self):
      "override (loop will be started automatically after this)"
      pass

   def teardown_asyncio_app(self):
      "override (loop will be stopped automatically after this)"
      pass


class WAMPComponentService(BaseAsyncioService):
   "base windows service for running a WAMP component"

   _svc_name_ = "WAMPService"
   _svc_display_name_ = "WAMP Service"
   _svc_description_ = "Windows service for running a WAMP component"

   wmp_url = None
   wmp_realm = None
   wmp_extra = None
   wmp_sessioncomponent = None
   wmp_serializers = None
   wmp_ssl = None #  set to True or False for forced enable/disable


   def _do_ssl(self, isSecureURL):
      "help determine whether we should use SSL"
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

      assert self.wmp_realm is not None

      cfg = ComponentConfig(self.wmp_realm, self.wmp_extra)

      # if component instantiation fails, stop the service
      try:
         session = self.wmp_sessioncomponent(cfg)
      except Exception:
         self.SvcStop()
      else:
         return session

   def main(self):
      txaio.use_asyncio()
      txaio.config.loop = asyncio.get_event_loop()
      BaseAsyncioService.main(self)

   def setup_asyncio_app(self):
      ""
      isSecureURL, host, port, resource, path, params = parse_url(self.wmp_url)
      make_transport = WampWebSocketClientFactory(self._component,
                                                  url=self.wmp_url,
                                                  serializers=self.wmp_serializers)
      ssl = self._do_ssl(isSecureURL)
      transport_coro = self.loop.create_connection(make_transport, host, port, ssl=ssl)
      (transport, self._protocol) = loop.run_until_complete(transport_coro)


   def teardown_asyncio_app(self):
      ""

