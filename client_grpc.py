import asyncio

from grpclib.client import Channel

import settings
from app.billing.grpc.pb2.billing_grpc import BillingServiceStub
from app.billing.grpc.pb2.billing_pb2 import RegisterRequest


async def main():
    channel = Channel(loop=asyncio.get_event_loop(), host=settings.GRPC_SERVER_HOST, port=settings.GRPC_SERVER_PORT)
    stub = BillingServiceStub(channel)

    reply = await stub.Register(RegisterRequest(
        name='jackdoe',
        country='Russia',
        city='Kursk',
        currency='EUR'
    ))
    print("REPLY HERE", reply, type(reply))

    channel.close()


if __name__ == '__main__':
    asyncio.run(main())
