import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import grpc
import asyncio
from concurrent import futures

from generated import crypto_pb2, crypto_pb2_grpc

from currency_exchange import currency_exchange_worker
from data_handle import (
    get_cryptos_data,
    get_crypto_data,
    crypto_data_worker,
    get_history_data,
)

import logging
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)


class CryptoService(crypto_pb2_grpc.CryptoServiceServicer):
    async def StreamTopCryptos(self, request, context):
        """
        Transmite las principales criptomonedas en una divisa específica, ordenadas por capitalización de mercado descendente.
        La transmisión continuará hasta que se detenga el servidor.

        args:
            request: Una solicitud CryptoRequest con la divisa y la cantidad a transmitir.
            context: El contexto gRPC.

        Return:
            Una lista CryptoList con las principales criptomonedas en la divisa especificada.
        """
        try:
            while not context.done():
                log.info("Transmitiendo criptomonedas...")

                data = get_cryptos_data(request.currency, request.quantity)
                yield crypto_pb2.CryptoList(cryptos=[c.to_proto() for c in data])
                await asyncio.sleep(30)

            log.info("Cliente desconectado del stream.")
        except Exception as e:
            log.error(f"Error en StreamTopCryptos: \n{e}")

    async def GetPriceHistory(self, request, context):
        try:
            raw_history = get_history_data(
                crypto_id=request.id,
                history_size=request.history_size,
                target_currency=request.currency,
            )

            # Convertir los puntos de dict a Proto
            proto_prices = [
                crypto_pb2.HistoricalPricePoint(
                    timestamp=point["timestamp"], price=point["price"]
                )
                for point in raw_history
            ]

            return crypto_pb2.HistoricalResponse(id=request.id, prices=proto_prices)
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.HistoricalResponse()

    async def GetTopCryptos(self, request, context):
        try:
            data = get_cryptos_data(request.currency, request.quantity)
            return crypto_pb2.CryptoList(cryptos=[c.to_proto() for c in data])
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.CryptoList(cryptos=[])

    async def GetCryptoById(self, request, context):
        try:
            data = get_crypto_data(request.id, request.currency)
            return data.to_proto()
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.Crypto()


async def serve():
    log.info("Iniciando el servidor...")

    # Comenzar tarea en segundo plano para actualizar los datos de criptomonedas
    worker_task = asyncio.create_task(crypto_data_worker(interval=30))
    currency_worker_task = asyncio.create_task(currency_exchange_worker(interval=60))

    # Comenzar servidor gRPC
    server = grpc.aio.server()
    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    crypto_pb2_grpc.add_CryptoServiceServicer_to_server(CryptoService(), server)

    RPC_ADDRESS = os.getenv("rpc-info", "127.0.0.1:50051")
    server.add_insecure_port(RPC_ADDRESS)
    await server.start()

    log.info("Servidor iniciado y worker iniciado.")

    try:
        await server.wait_for_termination()
    finally:
        log.info("Ctrl+C detectado. Cerrando servidor...")
        worker_task.cancel()
        currency_worker_task.cancel()
        await server.stop(grace=None)
        log.info("Worker de caché finalizado y servidor detenido.")
        print("\n--- PROCESO FINALIZADO ---")


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("Servidor detenido manualmente.")
