import os, sys, time, logging, asyncio, subprocess

from pytest import raises, mark, fixture

from asynciohelpers.testing import CrossbarRouter

from .services import BasicWindowsService, BasicWindowsAsyncioService, \
                      ConnectingWindowsAsyncioService, ReConnectingWindowsAsyncioService, \
                      WindowsWAMPService

from ..util import log_exception
from ..abcs import WindowsServiceABC

tested_services = (WindowsWAMPService,)


# Bare API implementation

class BareWindowsService(WindowsServiceABC):

   _svc_name_ = None
   _svc_display_name_ = None
   _svc_description_ = None

   def SvcDoRun(self):
      "called by Windows service manager to run the service"

   def SvcStop(self):
      "called by Windows service manager to stop the service"


@fixture(scope="module", params=tested_services)
def servicefactory(request):
   klass = request.param
   bases = list(klass.__bases__)
   bases.append(BareWindowsService)
   klass.__bases__ = tuple(bases)
   yield klass
   return

"""
def test_01_instantiate(servicefactory):
   "instantiation of service class works"

   s = servicefactory((servicefactory.__name__,))


@mark.asyncio
async def test_02_rejoin_realm(servicefactory, event_loop):

   server = servicefactory((servicefactory.__name__,))
   server.set_loop(event_loop)

   async with CrossbarRouter(event_loop) as cb:
      await server.start()

   print("\n --- restarting router ---- \n")

   await asyncio.sleep(2, loop=event_loop)

   async with CrossbarRouter(event_loop) as cb:
      await asyncio.sleep(2, loop=event_loop)
      await server.stop()

"""
