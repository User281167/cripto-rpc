import sys
import os
import grpc
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generated import crypto_pb2, crypto_pb2_grpc
from utils import ProjectEnv

load_dotenv()


class RpcInfoClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(ProjectEnv.RPC_INFO)
        self.stub = crypto_pb2_grpc.CryptoServiceStub(self.channel)

    async def get_top_cryptos(self, currency: str = "usd", quantity: int = 15):
        request = crypto_pb2.CryptoRequest(currency=currency, quantity=quantity)
        return self.stub.GetTopCryptos(request)

    async def get_crypto_by_id(self, id: str, currency: str = "usd"):
        request = crypto_pb2.CryptoByIdRequest(id=id, currency=currency)
        return self.stub.GetCryptoById(request)

    async def get_price_history(
        self, id: str, currency: str = "usd", history_size: int = 5
    ):
        request = crypto_pb2.HistoricalRequest(
            id=id, currency=currency, history_size=history_size
        )
        return self.stub.GetPriceHistory(request)

    async def stream_top_cryptos(self, currency: str = "usd", quantity: int = 5):
        request = crypto_pb2.CryptoRequest(currency=currency, quantity=quantity)
        return self.stub.StreamTopCryptos(request)


async def main():
    rpc = RpcInfoClient()

    top_task = asyncio.create_task(rpc.get_top_cryptos())
    bitcoin_task = asyncio.create_task(rpc.get_crypto_by_id("bitcoin"))
    history_task = asyncio.create_task(rpc.get_price_history("bitcoin"))

    print("Esperando resultados...")

    await asyncio.gather(top_task, bitcoin_task, history_task)

    print(top_task.result())
    print(bitcoin_task.result())
    print(history_task.result())

    stream = await rpc.stream_top_cryptos()

    for update in stream:
        print("Nueva actualización:")
        print(update.cryptos[0])
        print("------------------------")


if __name__ == "__main__":
    asyncio.run(main())
