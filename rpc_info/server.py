import grpc
from concurrent import futures

import crypto_pb2
import crypto_pb2_grpc

from data_handle import get_cryptos_data, get_crypto_data

import logging
from dotenv import load_dotenv
import os
import time

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)


class CryptoService(crypto_pb2_grpc.CryptoServiceServicer):
    def StreamTopCryptos(self, request, context):
        """
        Transmite las principales criptomonedas en una divisa específica, ordenadas por capitalización de mercado descendente.
        La transmisión continuará hasta que se detenga el servidor.

        args:
            request: Una solicitud CryptoRequest con la divisa y la cantidad a transmitir.
            context: El contexto gRPC.

        Return:
            Una lista CryptoList con las principales criptomonedas en la divisa especificada.
        """
        while context.is_active:
            data = get_cryptos_data(request.currency, request.quantity)
            yield crypto_pb2.CryptoList(cryptos=[c.to_proto() for c in data])
            time.sleep(10)

    def GetTopCryptos(self, request, context):
        try:
            data = get_cryptos_data()
            return crypto_pb2.CryptoList(cryptos=[c.to_proto() for c in data])
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.CryptoList(cryptos=[])

    def GetCryptoById(self, request, context):
        try:
            data = get_crypto_data(request.id)
            return crypto_pb2.Crypto(data.to_proto())
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
