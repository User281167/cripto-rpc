import grpc
from concurrent import futures

import crypto_pb2
import crypto_pb2_grpc

from data_handle import get_cryptos_data, get_crypto_data, clean_crypto_data

import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)


class CryptoService(crypto_pb2_grpc.CryptoServiceServicer):
    def GetTopCryptos(self, request, context):
        try:
            data = get_cryptos_data()
            data = clean_crypto_data(data)
            return crypto_pb2.CryptoList(cryptos=data)
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.CryptoList(cryptos=[])

    def GetCryptoById(self, request, context):
        try:
            data = get_crypto_data(request.id)
            return crypto_pb2.Crypto(**data)
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.Crypto()


def serve():
    log.info("Iniciando el servidor...")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    crypto_pb2_grpc.add_CryptoServiceServicer_to_server(CryptoService(), server)

    server.add_insecure_port(os.getenv("rpc-info", "127.0.0.1:50051"))
    server.start()

    log.info("Servidor iniciado.")
    server.wait_for_termination()
    log.info("Servidor finalizado.")


if __name__ == "__main__":
    serve()
