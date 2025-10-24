# modulos/data_handler.py
import requests
import pandas as pd


def obtener_datos_cripto(moneda="usd", cantidad=15):
    """Consume la API de CoinGecko para obtener datos de mercado de criptomonedas."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": moneda,
        "order": "market_cap_desc",
        "per_page": cantidad,
        "page": 1,
    }
    print(f"Obteniendo los {cantidad} principales activos en {moneda.upper()}...")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al consumir la API: {e}")
        return None


def procesar_datos(datos_api):
    """Limpia y organiza los datos crudos de la API en un DataFrame de Pandas."""
    if not datos_api:
        return None
    df = pd.DataFrame(datos_api)
    df_procesado = df[["name", "current_price", "price_change_percentage_24h"]].copy()
    df_procesado.rename(
        columns={
            "name": "Activo",
            "current_price": "Precio Actual (USD)",
            "price_change_percentage_24h": "Variacion % (24h)",
        },
        inplace=True,
    )
    return df_procesado
