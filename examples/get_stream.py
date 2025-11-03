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


# stream de datos
request = crypto_pb2.CryptoRequest(currency="cop", quantity=5)

try:
    for update in stub.StreamTopCryptos(request):
        print("Nueva actualización:")
        print(update.cryptos[0])
        print("------------------------")
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"Ocurrió un error: {e}")
