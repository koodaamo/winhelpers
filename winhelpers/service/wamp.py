from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
from autobahn.asyncio.websocket import WampWebSocketClientFactory
from autobahn.asyncio.wamp import ApplicationSession

from .async import BaseAsyncioTransportService


class BaseWAMPComponentService(BaseAsyncioTransportService):
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


   def _transport_connector(self):

      try:
         isSecureURL, host, port, resource, path, params = parse_url(self.wmp_url)
      except:
         raise Exception("could not parse WAMP router url '%s'" % self.wmp_url)

      try:
         factory = WampWebSocketClientFactory(self._component, url=self.wmp_url, serializers=self.wmp_serializers)
      except Exception as exc:
         raise Exception("could not build transport factory:" % str(exc))

      try:
         ssl = self._do_ssl(isSecureURL)
      except Exception as exc:
         raise Exception("ssl config parsing failed: %s" % str(exc))

      try:
         return self._loop.create_connection(factory, host, port, ssl=ssl)
      except:
         raise Exception("cannot instantiate transport coroutine: %s" % str(exc))


