"""
 Example services
"""

import os, sys, asyncio, logging

from asynciohelpers.service import AsyncioServiceBase
from asynciohelpers.service import AsyncioConnectingServiceBase
from asynciohelpers.service import AsyncioReConnectingServiceBase
from asynciohelpers.wamp import WAMPServiceMixin
from asynciohelpers.testing import TransportClientProtocol
from asynciohelpers.util import wamp_configured, wamp_env_configured, env_configured
from autobahn.asyncio.wamp import ApplicationSession

from ..util import servicemetadataprovider, eventloggerprovider
from ..service import WindowsServiceBase
from . import WAMP_ROUTER_URL, WAMP_ROUTER_REALM, WAMP_ROUTER_SSL, TEST_HOST, TEST_PORT


@eventloggerprovider
@servicemetadataprovider
class BasicWindowsService(WindowsServiceBase):
   "service that does basically nothing"


#
# Asyncio examples
#

@eventloggerprovider
@servicemetadataprovider
class BasicWindowsAsyncioService(AsyncioServiceBase, WindowsServiceBase):
   "service that does basically nothing but runs the loop"


@eventloggerprovider
class TransportProtocol(asyncio.Protocol):

   def connection_made(self, transport):
      self._logger.debug("connection made")

   def connection_lost(self, exc):
      self._logger.debug("connection lost")


@eventloggerprovider
@servicemetadataprovider
class ConnectingWindowsAsyncioService(AsyncioConnectingServiceBase, WindowsServiceBase):
   "service that connects a transport, reconnecting as necessary"

   _transport_factory = TransportProtocol



@eventloggerprovider
@servicemetadataprovider
class ReConnectingWindowsAsyncioService(AsyncioReConnectingServiceBase, WindowsServiceBase):
   "service that connects a transport, reconnecting as necessary"

   _transport_factory = TransportProtocol


@eventloggerprovider
@env_configured
@servicemetadataprovider
class EnvConfiguredReConnectingWindowsAsyncioService(AsyncioReConnectingServiceBase, WindowsServiceBase):
   "environment-configured service that connects a transport, reconnecting as necessary"

#
# WAMP example services
#


@eventloggerprovider
class WAMPComponent(ApplicationSession):
   ""

   def onJoin(self, details):
      self._transport._session_joined.set_result(True)
      self._logger.debug("joined realm")


@eventloggerprovider
@servicemetadataprovider
@wamp_configured
@wamp_env_configured
class WindowsWAMPService(WAMPServiceMixin, AsyncioReConnectingServiceBase, WindowsServiceBase):

   wmp_url = WAMP_ROUTER_URL
   wmp_realm = WAMP_ROUTER_REALM
   wmp_ssl = WAMP_ROUTER_SSL
   wmp_extra = None
   wmp_serializers = None

   wmp_sessioncomponent = WAMPComponent

