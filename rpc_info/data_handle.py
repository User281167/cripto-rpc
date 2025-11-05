import httpx
import asyncio
import requests
import logging
import time
from typing import List

from models import CryptoCurrency, CryptoHistoryItem
from currency_exchange import get_currency_exchange
from cache import DataCache, MAX_HISTORY_SIZE

log = logging.getLogger(__name__)


BASE_CURRENCY = "usd"
BASE_QUANTITY = 50


async def fetch_and_cache_data():
    """
    Obtiene los datos de criptomonedas de la API de CoinGecko y los guarda en un diccionario.
    """

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

            # Item de historial, precio e ID
            history_item = [
                CryptoHistoryItem(
                    id=c.id,
                    timestamp=int(time.time()),
                    price=c.current_price,
                )
                for c in new_data
            ]

            cache = DataCache()
            cache.save_crypto_data(new_data)
            cache.save_crypto_history(history_item)

            log.info(
                f"Cache actualizada con {len(new_data)} criptomonedas en {BASE_CURRENCY.upper()}"
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
    cache = DataCache()
    data = cache.get_crypto_data()[:quantity]

    log.info(f"Obteniendo {quantity} criptomonedas en {currency.upper()}...")

    if currency != BASE_CURRENCY and data:
        exchange = get_currency_exchange(currency)
        data = [c.update_price_factor(exchange) for c in data]

    return data


def get_history_data(
    crypto_id: str, history_size: int, target_currency: str
) -> list[CryptoHistoryItem]:
    """
    Obtiene los últimos N puntos de precio para una cripto,
    aplicando la conversión de moneda si es necesario.
    """

    cache = DataCache()
    history_size = min(history_size, MAX_HISTORY_SIZE)

    # Obtener los últimos N items del historial (Objetos CryptoHistoryItem)
    history_items: list[CryptoHistoryItem] = cache.get_crypto_history()
    history_items = list(filter(lambda item: item.id == crypto_id, history_items))
    history_items = history_items[-history_size:]

    if target_currency != BASE_CURRENCY:
        exchange_factor = get_currency_exchange(target_currency)
        history_items = [item.factor_price(exchange_factor) for item in history_items]

    return history_items


def get_crypto_data(coin_id: str, currency="usd") -> CryptoCurrency:
    # log.info(f"Obteniendo datos de {coin_id} en {currency.upper()}...")

    # url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}&include_24hr_change=true"
    # response = requests.get(url)
    # response.raise_for_status()

    # log.info("Datos obtenidos exitosamente.")

    # currency_exchange = get_currency_exchange(currency)
    # data = Currency.from_json(response.json()[0])

    # return data.update_price_factor(currency_exchange)
    cache = DataCache()
    data = cache.get_crypto_data()
    data = filter(lambda c: c.id == coin_id, data)

    if not data:
        raise Exception(f"No se encontraron datos para la cripto {coin_id}")

    data = list(data)[0]

    if currency != BASE_CURRENCY:
        exchange = get_currency_exchange(currency)
        data = data.update_price_factor(exchange)

    return data
