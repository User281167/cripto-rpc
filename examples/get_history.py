import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import grpc
from generated import crypto_pb2, crypto_pb2_grpc

from dotenv import load_dotenv
import os

load_dotenv()

channel = grpc.insecure_channel(os.getenv("rpc-info", "127.0.0.1:50051"))
stub = crypto_pb2_grpc.CryptoServiceStub(channel)

request = crypto_pb2.HistoricalRequest(id="bitcoin", currency="cop", history_size=5)
response = stub.GetPriceHistory(request)

print(response)
