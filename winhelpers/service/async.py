import asyncio
from .base import BaseService


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


class BaseAsyncioTransportService(BaseAsyncioService):
   "asyncio service that connects a transport"


   def _transport_connector(self):
      "return the transport connector coroutine"
      raise NotImplementedError()

   def _connect_transport(self):
      "run the transport connector"
      (transport, proto) = self._loop.run_until_complete(self._transport_connector())
      self._transport, self._protocol = transport, proto

   def setup_asyncio_app(self):
      "override (loop will be started automatically after this)"
      self._connect_transport()
