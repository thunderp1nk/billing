import argparse
import asyncio
import signal

from grpclib.server import Server

import settings
from app.billing.grpc.service import BillingService
from app.billing.models import init_engine


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('host', nargs='?', const=1, default=settings.GRPC_SERVER_HOST)
    p.add_argument('port', nargs='?', type=int, const=1, default=settings.GRPC_SERVER_PORT)
    args = p.parse_args()
    host = args.host
    port = args.port

    env = server = None
    loop = asyncio.get_event_loop()

    try:
        engine = loop.run_until_complete(init_engine())
        server = Server([BillingService(engine=engine)], loop=asyncio.get_event_loop())
        loop.run_until_complete(server.start(host, port))
        stop = asyncio.Future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        loop.run_until_complete(stop)
    except KeyboardInterrupt:
        pass
    finally:
        server.close() if server else None
        engine = loop.run_until_complete(engine.close())
        loop.run_until_complete(server.wait_closed()) if server else None
