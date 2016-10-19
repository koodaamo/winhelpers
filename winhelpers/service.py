import sys, asyncio

import win32service
import win32serviceutil
import win32event
import servicemanager

from servicemanager import LogMsg, LogErrorMsg, LogInfoMsg, LogWarningMsg

from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
from autobahn.asyncio.websocket import WampWebSocketClientFactory
from autobahn.asyncio.wamp import ApplicationSession


class BaseService(win32serviceutil.ServiceFramework):

   _svc_name_ = "BaseService"
   _svc_display_name_ = "Base service helper"
   _svc_description_ = "A subclassable service base class"

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.ReportServiceStatus(win32service.SERVICE_START_PENDING, waitHint=60000)
      self.log_evt(servicemanager.PYS_SERVICE_STARTING)
      self._stop_event = win32event.CreateEvent(None, 0, 0, None)


   def log_evt(self, evtid):
      "convenience for logging the service lifecycle events"
      LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, evtid, (self._svc_display_name_, ''))


   def main(self):
      "dummy main that just waits for the stop event"
      win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)

   def SvcDoRun(self):
      "service controller is telling us to start; let's comply"

      LogInfoMsg("%s service start requested" % self._svc_name_)

      # log start to event log and report to service controller
      self.log_evt(servicemanager.PYS_SERVICE_STARTED)
      self.ReportServiceStatus(win32service.SERVICE_RUNNING)

      # let the main app do its job; it has to block and return cleanly at exit
      self.main()

      # log stop to event log and report to service controller
      self.ReportServiceStatus(win32service.SERVICE_STOPPED)
      self.log_evt(servicemanager.PYS_SERVICE_STOPPED)


   def SvcStop(self):
      "the service controller is shutting us down, so trigger the stop event"
      LogInfoMsg("%s: service stop called" % self._svc_name_)
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self._stop_event)


class BaseAsyncioService(BaseService):
   "base windows service that handles loop management etc."

   _svc_name_ = "BaseAsyncioService"
   _svc_display_name_ = "Base asyncio service helper"
   _svc_description_ = "A subclassable service for running an asyncio loop"


   def _exception_handler(self, loop, data):
      LogErrorMsg("%s: exception: %s" % (self._svc_name_, str(data)))


   def main(self):
      "loop until stopped"

      self.loop = loop = asyncio.get_event_loop()
      loop.set_exception_handler(self._exception_handler)

      # let the app prepare itself
      try:
         self.setup_asyncio_app()
      except Exception as exc:
         LogErrorMsg("%s asyncio setup failed, not starting: %s" % (self._svc_name_, str(exc)))
      else:

         # create service stop waiter and run the loop
         def waiter():
            win32event.WaitForSingleObject(self._stop_event, win32event.INFINITE)

         stop_waiter_future = loop.run_in_executor(None, waiter)
         loop.run_until_complete(stop_waiter_future)

      # let app try tear itself apart, regardless of whether it ever run properly
      try:
         self.teardown_asyncio_app()
      except Exception as exc:
         LogErrorMsg("%s asyncio teardown failed, exiting: %s" % (self._svc_name_, str(exc)))

      loop.stop()
      loop.close()

   def setup_asyncio_app(self):
      "override (loop will be started automatically after this)"
      pass

   def teardown_asyncio_app(self):
      "override (loop will be stopped automatically after this)"
      pass


class WAMPComponentService(BaseAsyncioService):
   "base windows service for running a WAMP component"

   _svc_name_ = "BaseWAMPService"
   _svc_display_name_ = "Base WAMP service helper"
   _svc_description_ = "Base Windows service for running a WAMP component"

   wmp_url = None
   wmp_realm = None
   wmp_sessioncomponent = None
   wmp_serializers = None
   wmp_ssl = None #  set to True or False for forced enable/disable
   wmp_extra = {"service": True} # we are running as a Windows service

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

      try:
         cfg = ComponentConfig(self.wmp_realm, self.wmp_extra)
      except Exception as exc:
         raise Exception("could not instantiate WAMP component config: %s" % str(exc))

      # if component instantiation fails, stop the service
      try:
         session = self.wmp_sessioncomponent(cfg)
      except Exception as exc:
         raise Exception("could not instantiate WAMP component: %s" % str(exc))
      else:
         return session


   def setup_asyncio_app(self):
      "establish the transport"

      try:
         isSecureURL, host, port, resource, path, params = parse_url(self.wmp_url)
      except:
         raise Exception("could not parse WAMP router url '%s'" % self.wmp_url)

      try:
         make_transport = WampWebSocketClientFactory(self._component, url=self.wmp_url, serializers=self.wmp_serializers)
      except Exception as exc:
         raise Exception("could not build transport factory:" % str(exc))

      try:
         ssl = self._do_ssl(isSecureURL)
      except Exception as exc:
         raise Exception("ssl config parsing failed: %s" % str(exc))

      try:
         transport_coro = self.loop.create_connection(make_transport, host, port, ssl=ssl)
      except:
         raise Exception("cannot instantiate transport coroutine: %s" % str(exc))

      try:
         (transport, self._protocol) = self.loop.run_until_complete(transport_coro)
      except Exception as exc:
         raise Exception("connection to router failed, is remote server up?")

      LogInfoMsg("%s asyncio setup complete" % self._svc_name_)


   def teardown_asyncio_app(self):
      ""
      LogInfoMsg("%s asyncio teardown complete" % self._svc_name_)


# These are for testing purposes only

class DummyWAMPComponent(ApplicationSession):

   async def onJoin(self, details):
      servicemanager.LogInfoMsg("%s: connection made" % self.__class__.__name__)


class DummyWAMPService(WAMPComponentService):

   _svc_name_ = "DummyWAMPTestService"
   _svc_display_name_ = "Dummy WAMP test service"
   _svc_description_ = "Dummy WAMP service used in winhelpers testing"

   wmp_url = "ws://10.211.55.4:8080/ws"
   wmp_realm = "realm1"
   wmp_sessioncomponent = DummyWAMPComponent
