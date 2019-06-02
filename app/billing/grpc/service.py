from app.billing.grpc.pb2.billing_grpc import BillingServiceBase
from app.billing.grpc.pb2.billing_pb2 import SuccessReply
from app.billing.service_layers import Register


class BillingService(BillingServiceBase):

    def __init__(self, engine):
        self.engine = engine

    async def Register(self, stream):
        # для примера, тут нужно немало дорабатывать, чтоб было красиво :)
        request = await stream.recv_message()

        async with self.engine.acquire() as conn:
            await Register(
                name=request.name,
                country=request.country,
                city=request.city,
                currency=request.currency,
            ).execute(conn)

        await stream.send_message(SuccessReply())
