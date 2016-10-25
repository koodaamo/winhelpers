"""TEST SERVERS"""

import os, asyncio
import servicemanager
from autobahn.asyncio.wamp import ApplicationSession

from . import *


class DummyService(BaseService):
   ""
   _svc_name_ = "DummyService"
   _svc_display_name_ = "Dummy test service"
   _svc_description_ = "Dummy service used in winhelpers testing"


class DummyAsyncioService(BaseAsyncioService):
   ""
   _svc_name_ = "DummyAsyncioService"
   _svc_display_name_ = "Dummy Asyncio test service"
   _svc_description_ = "Dummy Asyncio service used in winhelpers testing"


class DummyTransportProtocol(asyncio.Protocol):

   def connection_made(self, transport):
      ""

   def connection_lost(self, exc):
      ""

class DummyAsyncioTransportService(BaseAsyncioTransportService):
   ""

   def _transport_connector(self):
      "return the transport connector coroutine"
      HOST = os.environ.get("TEST_HOST")
      PORT = os.environ.get("TEST_PORT")
      return self._loop.create_connection(DummyTransportProtocol, host=HOST, port=PORT)


class DummyWAMPComponent(ApplicationSession):
   ""

   async def onJoin(self, details):
      servicemanager.LogInfoMsg("%s: connection made" % self.__class__.__name__)


class DummyWAMPService(BaseWAMPComponentService):

   _svc_name_ = "DummyWAMPTestService"
   _svc_display_name_ = "Dummy WAMP test service"
   _svc_description_ = "Dummy WAMP service used in winhelpers testing"

   @property
   def wmp_url(self):
      return "ws://%s/ws" % os.environ.get("TEST_ROUTER")

   wmp_realm = "realm1"
   wmp_sessioncomponent = DummyWAMPComponent

