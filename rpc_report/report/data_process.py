import os
import hashlib
import logging
import pandas as pd
from datetime import datetime

from models import CryptoCurrency
from .generate_crypto_report import generate_crypto_report

log = logging.getLogger(__name__)


def crypto_data_to_df(data: list[CryptoCurrency]) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame([CryptoCurrency.to_dict(c) for c in data])
    df = df[["name", "current_price", "price_change_percentage_24h"]]

    return df


def generate_report_hash(
    currency: str, timestamp: datetime, interval_minutes: int = 60
) -> str:
    # Truncar el tiempo al intervalo más cercano
    rounded = timestamp.replace(
        minute=(timestamp.minute // interval_minutes) * interval_minutes,
        second=0,
        microsecond=0,
    )
    key = f"{currency}-{rounded.isoformat()}"
    return hashlib.sha256(key.encode()).hexdigest()


def get_cached_report_path(report_hash: str, folder=".reports/crypto") -> str:
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{report_hash}.xlsx")


def create_and_get_crypto_report(
    data: list[CryptoCurrency], currency="usd", interval_minutes=60
):
    """
    Genera o reutiliza un reporte de criptomonedas en Excel.

    Returns:
        filename (str): Nombre del archivo generado o reutilizado.
        content (bytes): Contenido binario del archivo.
    """
    now = datetime.utcnow()
    report_hash = generate_report_hash(currency, now, interval_minutes)
    filepath = get_cached_report_path(report_hash)

    if os.path.exists(filepath):
        log.info(f"Usando reporte en caché: {filepath}")
    else:
        log.info(f"Generando nuevo reporte: {filepath}")

        data_frame = crypto_data_to_df(data)
        generate_crypto_report(data, data_frame, filepath)
        log.info(f"Reporte generado exitosamente en '{filepath}'")

    with open(filepath, "rb") as f:
        content = f.read()

    return filepath, content
