import requests
import logging

from crypto_currency import CryptoCurrency

log = logging.getLogger(__name__)


def get_cryptos_data(currency="usd", quantity=15):
    """Consume la API de CoinGecko para obtener datos de mercado de criptomonedas."""

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": quantity,
        "page": 1,
    }

    log.info(f"Obteniendo los {quantity} principales activos en {currency.upper()}...")

    response = requests.get(url, params=params)
    response.raise_for_status()

    log.info("Datos obtenidos exitosamente.")

    cryptos = []

    for crypto in response.json():
        cryptos.append(CryptoCurrency.from_dict(crypto))

    return cryptos


def get_crypto_data(coin_id, currency="usd"):
    log.info(f"Obteniendo datos de {coin_id} en {currency.upper()}...")

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}&include_24hr_change=true"
    response = requests.get(url)
    response.raise_for_status()

    log.info("Datos obtenidos exitosamente.")

    cryptos = []

    for crypto in response.json():
        cryptos.append(CryptoCurrency.from_dict(crypto))

    return response.json()


if __name__ == "__main__":
    data = get_cryptos_data()
    print(data)
