from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
from autobahn.asyncio.websocket import WampWebSocketClientFactory
from autobahn.asyncio.wamp import ApplicationSession

from .async import BaseAsyncioService


class BaseWAMPComponentService(BaseAsyncioService):
   "base windows service for running a WAMP component that connects to a router"

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


