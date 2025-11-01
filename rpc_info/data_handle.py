import requests
import logging

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
    return response.json()


def get_crypto_data(coin_id, currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}&include_24hr_change=true"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def clean_crypto_data(data):
    # Lista de claves que quieres eliminar
    keys_to_remove = [
        "market_cap_change_24h",
        "market_cap_change_percentage_24h",
        "circulating_supply",
        "total_supply",
        "max_supply",
        "ath",
        "ath_change_percentage",
        "ath_date",
        "atl",
        "atl_change_percentage",
        "atl_date",
        "roi",
    ]

    # Filtrar cada diccionario en la lista
    cleaned_data = []

    for item in data:
        cleaned_item = {k: v for k, v in item.items() if k not in keys_to_remove}
        cleaned_data.append(cleaned_item)

    return cleaned_data


if __name__ == "__main__":
    data = get_cryptos_data()
    data = clean_crypto_data(data)
    print(data)
