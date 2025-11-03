import requests
import asyncio
import httpx
import logging

log = logging.getLogger(__name__)

# En base a USD
_CURRENCY_EXCHANGE = {"data": []}
CURRENCY_EXCHANGE_API_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2025.11.1/v1/currencies/usd.json"


async def fetch_currency_exchange():
    """
    Obtener el cambio de moneda
    """
    global _CURRENCY_EXCHANGE

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            log.info("Obteniendo cambio de moneda...")

            response = await client.get(CURRENCY_EXCHANGE_API_URL)
            response.raise_for_status()

            data = response.json()
            _CURRENCY_EXCHANGE["data"] = response.json()["usd"]
            return _CURRENCY_EXCHANGE["data"]
    except httpx.HTTPStatusError as e:
        log.error(f"HTTP Error obteniendo cambio de moneda: {e}")
    except Exception as e:
        log.error(f"Error obteniendo cambio de moneda: {e}")


async def currency_exchange_worker(interval=600):
    """
    Actualizar el cambio de moneda

    Args:
        timeout (int): Tiempo de espera en segundos.
    """
    global _CURRENCY_EXCHANGE

    while True:
        await fetch_currency_exchange()
        await asyncio.sleep(interval)


def get_currency_exchange(target_currency="EUR") -> float:
    """
    Obtener el cambio de moneda
    """
    try:
        return _CURRENCY_EXCHANGE["data"][target_currency.lower()]
    except Exception as e:
        log.error(f"Error obteniendo cambio de moneda: {e}")
        return 0
