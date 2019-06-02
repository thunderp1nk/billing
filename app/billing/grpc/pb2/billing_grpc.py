# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: billing.proto
# plugin: grpclib.plugin.main
import abc
import typing

import grpclib.const
import grpclib.client
if typing.TYPE_CHECKING:
    import grpclib.server

from app.billing.grpc.pb2 import billing_pb2


class BillingServiceBase(abc.ABC):

    @abc.abstractmethod
    async def Register(self, stream: 'grpclib.server.Stream[billing_pb2.RegisterRequest, billing_pb2.SuccessReply]') -> None:
        pass

    def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:
        return {
            '/BillingService/Register': grpclib.const.Handler(
                self.Register,
                grpclib.const.Cardinality.UNARY_UNARY,
                billing_pb2.RegisterRequest,
                billing_pb2.SuccessReply,
            ),
        }


class BillingServiceStub:

    def __init__(self, channel: grpclib.client.Channel) -> None:
        self.Register = grpclib.client.UnaryUnaryMethod(
            channel,
            '/BillingService/Register',
            billing_pb2.RegisterRequest,
            billing_pb2.SuccessReply,
        )