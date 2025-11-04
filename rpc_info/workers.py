"""
Workers en segundo plano para actualizar los datos de criptomonedas

Permite tener solo una instancia para obtener los datos.
Permite que N servidores obtengan los datos de criptomonedas en segundo plano sin problemas de condiciones de carrera
"""

import os
import sys
import asyncio
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import ProjectEnv
from cache import DataCache
from data_handle import crypto_data_worker
from currency_exchange import currency_exchange_worker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


async def start_workers():
    logging.info("Iniciando workers...")

    cache = DataCache(
        host=ProjectEnv.RPC_INFO_REDIS_HOST,
        port=ProjectEnv.RPC_INFO_REDIS_PORT,
    )

    try:
        asyncio.create_task(crypto_data_worker(interval=30))
        asyncio.create_task(currency_exchange_worker(interval=600))

        logging.info("Workers iniciados.")

        # Esperar indefinidamente
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logging.info("Workers detenidos.")
    finally:
        logging.info("Cerrando workers...")
        cache.close()

    logging.info("Workers finalizados.")


if __name__ == "__main__":
    try:
        asyncio.run(start_workers())
    except KeyboardInterrupt:
        logging.info("Deteniendo workers...")
