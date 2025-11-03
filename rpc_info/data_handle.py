import httpx
import asyncio
import requests
import logging
import time
from typing import List

from crypto_currency import CryptoCurrency, CryptoHistoryItem
from currency_exchange import get_currency_exchange

log = logging.getLogger(__name__)

_CRYPTO_CACHE = {
    "data": [],
    "history": [],
    "last_updated": 0,
}

BASE_CURRENCY = "usd"
BASE_QUANTITY = 50
MAX_HISTORY_SIZE = (
    24 * 60 * 60 // 30
)  # 24 horas de datos, actualizados cada 30 segundos


async def fetch_and_cache_data():
    """
    Obtiene los datos de criptomonedas de la API de CoinGecko y los guarda en un diccionario.
    """
    global _CRYPTO_CACHE

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": BASE_CURRENCY,
        "order": "market_cap_desc",
        "per_page": BASE_QUANTITY,
        "page": 1,
    }

    log.info("Obteniendo datos de criptomonedas de la API CoinGecko...")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            raw_data = response.json()
            new_data = [CryptoCurrency.from_json(d) for d in raw_data]

            current_time = int(time.time())

            # Item de historial, precio e ID
            history_item = CryptoHistoryItem.from_raw_data(raw_data)

            _CRYPTO_CACHE["data"] = new_data

            if len(_CRYPTO_CACHE["history"]) >= MAX_HISTORY_SIZE:
                _CRYPTO_CACHE["history"].pop(0)

            _CRYPTO_CACHE["history"].append(history_item)
            _CRYPTO_CACHE["last_updated"] = current_time
            log.info(
                f"Cache actualizada. History size: {len(_CRYPTO_CACHE['history'])}"
            )
    except httpx.HTTPStatusError as e:
        log.error(f"HTTP Error obteniendo data: {e.response.status_code}")
    except Exception as e:
        log.error(f"Error obteniendo y guardando en cache los datos: {e}")


async def crypto_data_worker(interval=60):
    """
    Función asíncrona que obtiene los datos de criptomonedas y los guarda en un diccionario.

    Args:
        interval (int): Intervalo en segundos en el que se obtienen los datos de criptomonedas.
    """

    while True:
        await fetch_and_cache_data()
        await asyncio.sleep(interval)


def get_cryptos_data(currency="usd", quantity=15) -> List[CryptoCurrency]:
    data = _CRYPTO_CACHE["data"][:quantity]

    log.info(f"Obteniendo {quantity} criptomonedas en {currency.upper()}...")

    if currency != BASE_CURRENCY and data:
        exchange = get_currency_exchange(currency)
        data = [c.update_price_factor(exchange) for c in data]

    return data


def get_history_data(
    crypto_id: str, history_size: int, target_currency: str
) -> list[dict]:
    """
    Obtiene los últimos N puntos de precio para una cripto,
    aplicando la conversión de moneda si es necesario.
    """

    # Obtener los últimos N items del historial (Objetos CryptoHistoryItem)
    history_items: list[CryptoHistoryItem] = _CRYPTO_CACHE["history"][-history_size:]

    exchange_factor = 1.0

    if target_currency != BASE_CURRENCY:
        exchange_factor = get_currency_exchange(target_currency)

    final_history_points = []

    # Filtrar y aplicar el factor de conversión.
    for item in history_items:
        point = item.to_historical_point(crypto_id, exchange=exchange_factor)

        if point:
            final_history_points.append(point)

    return final_history_points


def get_crypto_data(coin_id: str, currency="usd") -> CryptoCurrency:
    # log.info(f"Obteniendo datos de {coin_id} en {currency.upper()}...")

    # url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}&include_24hr_change=true"
    # response = requests.get(url)
    # response.raise_for_status()

    # log.info("Datos obtenidos exitosamente.")

    # currency_exchange = get_currency_exchange(currency)
    # data = Currency.from_json(response.json()[0])

    # return data.update_price_factor(currency_exchange)

    data = _CRYPTO_CACHE["data"]
    data = filter(lambda c: c.id == coin_id, data)

    if not data:
        raise Exception(f"No se encontraron datos para la cripto {coin_id}")

    data = list(data)[0]

    if currency != BASE_CURRENCY:
        exchange = get_currency_exchange(currency)
        data = data.update_price_factor(exchange)

    return data
