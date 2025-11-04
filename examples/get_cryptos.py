import sys
import os
import grpc
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import ProjectEnv
from generated import crypto_pb2, crypto_pb2_grpc


load_dotenv()

channel = grpc.insecure_channel(ProjectEnv.RPC_INFO)
stub = crypto_pb2_grpc.CryptoServiceStub(channel)

request = crypto_pb2.CryptoRequest(currency="usd", quantity=5)
response = stub.GetTopCryptos(request)

for crypto in response.cryptos:
    print(crypto.id, crypto.name, crypto.current_price)
