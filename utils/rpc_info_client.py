import sys
import os
import grpc
import grpc.aio
import asyncio
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generated import crypto_pb2, crypto_pb2_grpc
from .env import ProjectEnv


class RpcInfoClient:
    def __init__(self, async_mode=False):
        """
        Args:
            async_mode (bool): Comunicación asíncrona o sincrona.
                Defaults to False.
                TRUE: Asíncrono se debe usar async en cada función ya que se devuelve una coroutine.
        """
        if async_mode:
            self.channel = grpc.aio.insecure_channel(ProjectEnv.RPC_INFO)
        else:
            self.channel = grpc.insecure_channel(ProjectEnv.RPC_INFO)

        self.stub = crypto_pb2_grpc.CryptoServiceStub(self.channel)

    def get_top_cryptos(self, currency: str = "usd", quantity: int = 50):
        request = crypto_pb2.CryptoRequest(currency=currency, quantity=quantity)
        return self.stub.GetTopCryptos(request)

    def get_crypto_by_id(self, id: str, currency: str = "usd"):
        request = crypto_pb2.CryptoByIdRequest(id=id, currency=currency)
        return self.stub.GetCryptoById(request)

    def get_price_history(self, id: str, currency: str = "usd", history_size: int = 5):
        request = crypto_pb2.HistoricalRequest(
            id=id, currency=currency, history_size=history_size
        )
        return self.stub.GetPriceHistory(request)

    def stream_top_cryptos(self, currency: str = "usd", quantity: int = 5):
        request = crypto_pb2.CryptoRequest(currency=currency, quantity=quantity)
        return self.stub.StreamTopCryptos(request)
