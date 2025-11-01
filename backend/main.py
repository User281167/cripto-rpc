import grpc
import crypto_pb2
import crypto_pb2_grpc

from dotenv import load_dotenv
import os

load_dotenv()

channel = grpc.insecure_channel(os.getenv("rpc-info", "127.0.0.1:50051"))
stub = crypto_pb2_grpc.CryptoServiceStub(channel)

request = crypto_pb2.CryptoRequest(currency="usd", quantity=5)
response = stub.GetTopCryptos(request)

for crypto in response.cryptos:
    print(crypto.name, crypto.current_price)
