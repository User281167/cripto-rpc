import sys
import os
import grpc
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generated import crypto_pb2, crypto_pb2_grpc
from utils import ProjectEnv

load_dotenv()

channel = grpc.insecure_channel(ProjectEnv.RPC_INFO)
stub = crypto_pb2_grpc.CryptoServiceStub(channel)

request = crypto_pb2.CryptoByIdRequest(id="bitcoin", currency="usd")
response = stub.GetCryptoById(request)

print(response)
