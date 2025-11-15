import requests
import asyncio
import httpx
import logging

from cache import DataCache
from models import ExchangeRate

log = logging.getLogger(__name__)

# En base a USD
CURRENCY_EXCHANGE_API_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2025.11.1/v1/currencies/usd.json"


async def fetch_currency_exchange() -> dict | None:
    """
    Obtener el cambio de moneda
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            log.info("Obteniendo cambio de moneda...")

            response = await client.get(CURRENCY_EXCHANGE_API_URL)
            response.raise_for_status()

            data = response.json()

            cache = DataCache()
            cache.save_exchange(data["usd"])
            return data
    except httpx.HTTPStatusError as e:
        log.error(f"HTTP Error obteniendo cambio de moneda: {e}")
    except Exception as e:
        log.error(f"Error obteniendo cambio de moneda: {e}")

    return None


async def currency_exchange_worker(interval=600):
    """
    Actualizar el cambio de moneda

    Args:
        timeout (int): Tiempo de espera en segundos.
    """
    while True:
        await fetch_currency_exchange()
        await asyncio.sleep(interval)


def get_currency_exchange(target_currency="EUR") -> float:
    """
    Obtener el cambio de moneda
    """
    log.info(f"Obteniendo cambio de moneda para {target_currency.upper()}...")

    try:
        cache = DataCache()
        return cache.get_exchange()[target_currency.lower()]
    except Exception as e:
        log.error(f"Error obteniendo cambio de moneda: {e}")
        return 0


def get_exchanges() -> list[ExchangeRate]:
    cache = DataCache()
    data = cache.get_exchange()

    if not data:
        return []

    data = [ExchangeRate.from_dict(d) for d in data.items()]
    return data
