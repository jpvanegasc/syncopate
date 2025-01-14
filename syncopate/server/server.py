from syncopate.logging import logger
from syncopate.loop import EventLoop
from syncopate.server.protocol import HTTPProtocol


class HTTPServer:
    def __init__(self, app, host, port):
        self.app = app
        self.host = host
        self.port = port
        # TODO: create helper function to avoid instantiating EventLoop here
        self.loop = EventLoop()

    def serve(self):
        def protocol_factory():
            return HTTPProtocol(self.app, self.loop)

        server = self.loop.create_server(protocol_factory, self.host, self.port)
        logger.info("Server listening on %s:%s", self.host, self.port)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        except Exception:
            logger.exception("Error running server")
        finally:
            server.close()
            # TODO: add shutdown_asyncgens method to EventLoop
            self.loop.close()
            logger.info("Server closed")
