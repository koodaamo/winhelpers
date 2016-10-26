"""TEST SERVERS"""

import os, asyncio, sys
from servicemanager import LogInfoMsg, LogErrorMsg
from autobahn.asyncio.wamp import ApplicationSession

from . import *

def log_exception(exctype, value, tb):
   LogErrorMsg("%s (%s): %s" % (exctype, value, tb))

sys.excepthook = log_exception


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

   _svc_name_ = "DummyAsyncioTransportService"
   _svc_display_name_ = "Dummy Asyncio transport test service"
   _svc_description_ = "Dummy Asyncio transport service used in winhelpers testing"

   def _transport_connector(self):
      "return the transport connector coroutine"
      HOST = os.environ.get("TEST_HOST")
      PORT = os.environ.get("TEST_PORT")
      assert (HOST and PORT), "TEST_HOST or TEST_PORT variable not in environment: %s" % ', '.join(os.environ.keys())
      return self._loop.create_connection(DummyTransportProtocol, host=HOST, port=PORT)


class DummyWAMPComponent(ApplicationSession):
   ""

   def onJoin(self, details):
      LogInfoMsg("%s: joined realm" % self.__class__.__name__)


class DummyWAMPService(BaseWAMPComponentService):

   _svc_name_ = "DummyWAMPTestService"
   _svc_display_name_ = "Dummy WAMP test service"
   _svc_description_ = "Dummy WAMP service used in winhelpers testing"

   @property
   def wmp_url(self):
      url = os.environ.get("TEST_ROUTER_URL")
      LogInfoMsg("%s: using ws URL '%s'" % (self.__class__.__name__, url))
      return url

   wmp_realm = "realm1"
   wmp_sessioncomponent = DummyWAMPComponent

