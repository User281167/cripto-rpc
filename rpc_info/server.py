import os
import sys
import time
import grpc
import logging
import asyncio
from concurrent import futures

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import ProjectEnv
from generated import crypto_pb2, crypto_pb2_grpc
from cache import DataCache
from currency_exchange import get_exchanges
from data_handle import (
    get_cryptos_data,
    get_crypto_data,
    get_history_data,
)


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
            log.info(f"Obteniendo historial de precios {request}")

            history = get_history_data(
                crypto_id=request.id,
                history_size=request.history_size,
                target_currency=request.currency,
            )

            # Convertir los puntos de dict a Proto
            proto_prices = [
                crypto_pb2.HistoricalPricePoint(timestamp=p.timestamp, price=p.price)
                for p in history
            ]

            return crypto_pb2.HistoricalResponse(id=request.id, prices=proto_prices)
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.HistoricalResponse()

    async def GetTopCryptos(self, request, context):
        log.info(f"Obteniendo criptomonedas {request}")

        try:
            data = get_cryptos_data(request.currency, request.quantity)
            return crypto_pb2.CryptoList(cryptos=[c.to_proto() for c in data])
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.CryptoList(cryptos=[])

    async def GetCryptoById(self, request, context):
        log.info(f"Obteniendo criptomonedas {request}")

        try:
            data = get_crypto_data(request.id, request.currency)
            return data.to_proto()
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.Crypto()

    async def GetExchangeRates(self, request, context):
        log.info(f"Obteniendo cambio de divisas {request}")

        try:
            data = [r.to_proto() for r in get_exchanges()]
            return crypto_pb2.ExchangeRates(rates=data)
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            return crypto_pb2.ExchangeRates()


async def serve():
    log.info("Iniciando el servidor...")

    cache = DataCache(
        host=ProjectEnv.RPC_INFO_REDIS_HOST, port=ProjectEnv.RPC_INFO_REDIS_PORT
    )

    # Comenzar servidor gRPC
    server = grpc.aio.server()
    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    crypto_pb2_grpc.add_CryptoServiceServicer_to_server(CryptoService(), server)

    server.add_insecure_port(ProjectEnv.RPC_INFO)
    await server.start()

    log.info("Servidor iniciado.")

    try:
        await server.wait_for_termination()
    finally:
        log.info("Ctrl+C detectado. Cerrando servidor...")
        cache.close()
        await server.stop(grace=None)
        print("\n--- PROCESO FINALIZADO ---")


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("Servidor detenido manualmente.")
