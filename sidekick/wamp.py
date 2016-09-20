import txaio
from autobahn.asyncio.wamp import ApplicationRunner
from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.util import parse_url
from autobahn.asyncio.websocket import WampWebSocketClientFactory


class ServiceRunner(ApplicationRunner):

    def run(self, make):
        "'make' callable produces instances of ApplicationSession, given ComponentConfig"

        # factory for use ApplicationSession
        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = make(cfg)
            except Exception:
                self.log.failure("App session could not be created! ")
                asyncio.get_event_loop().stop()
            else:
                return session

        isSecure, host, port, resource, path, params = parse_url(self.url)

        if self.ssl is None:
            ssl = isSecure
        else:
            if self.ssl and not isSecure:
                raise RuntimeError(
                    'ssl argument value passed to %s conflicts with the "ws:" '
                    'prefix of the url argument. Did you mean to use "wss:"?' %
                    self.__class__.__name__)
            ssl = self.ssl

        # create a WAMP-over-WebSocket transport client factory
        transport_factory = WampWebSocketClientFactory(create, url=self.url, serializers=self.serializers)

        # start the client
        loop = asyncio.get_event_loop()
        txaio.use_asyncio()
        txaio.config.loop = loop
        coro = loop.create_connection(transport_factory, host, port, ssl=ssl)
        (transport, protocol) = loop.run_until_complete(coro)

        # start logging
        txaio.start_logging(level='info')

        def waitress(waited_for=self.stop_event, loop=loop):
            win32event.WaitForSingleObject(waited_for, win32event.INFINITE)
            loop.stop()
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            loop.close()

        stop_waitress = asyncio.ensure_future(loop.run_in_executor(None, waitress))

        # give Goodbye message a chance to go through, if we still
        # have an active session
        if protocol._session:
            loop.run_until_complete(protocol._session.leave())

        loop.close()
