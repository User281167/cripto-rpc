import os
import hashlib
import logging
import tempfile
import pandas as pd
from datetime import datetime

from models import CryptoCurrency

from .generate_crypto_report import generate_crypto_report
from .generate_trend_report import generate_trend_report
from .generate_executive_report import generate_executive_report

from .plot_data import save_bar_graph_as_image

log = logging.getLogger(__name__)


def crypto_data_to_df(data: list[CryptoCurrency]) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame([CryptoCurrency.to_dict(c) for c in data])
    df = df[["name", "current_price", "price_change_percentage_24h"]]

    return df


def generate_report_hash(
    currency: str, timestamp: datetime, interval_minutes: int = 60, extra: str = ""
) -> str:
    # Truncar el tiempo al intervalo más cercano
    rounded = timestamp.replace(
        minute=(timestamp.minute // interval_minutes) * interval_minutes,
        second=0,
        microsecond=0,
    )
    key = f"{currency}-{rounded.isoformat()}-{extra}"
    return hashlib.sha256(key.encode()).hexdigest()


def get_cached_report_path(
    report_hash: str, folder=".reports/crypto", suffix=".xlsx"
) -> str:
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{report_hash}{suffix}")


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
    report_hash = generate_report_hash(currency, now, interval_minutes, "excel")
    filepath = get_cached_report_path(report_hash, suffix=".xlsx")

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


def create_and_get_trend_report(
    data: list[CryptoCurrency], currency="usd", interval_minutes=60
):
    """
    Genera o reutiliza un reporte de tendencias en Word

    Returns:
        filename (str): Nombre del archivo generado o reutilizado.
        content (bytes): Contenido binario del archivo.
    """
    now = datetime.utcnow()
    report_hash = generate_report_hash(currency, now, interval_minutes, "word")
    filepath = get_cached_report_path(report_hash, suffix=".docx")

    if os.path.exists(filepath):
        log.info(f"Usando reporte en caché: {filepath}")
    else:
        log.info(f"Generando nuevo reporte: {filepath}")

        data_frame = crypto_data_to_df(data)
        generate_trend_report(data_frame, filepath)
        log.info(f"Reporte generado exitosamente en '{filepath}'")

    with open(filepath, "rb") as f:
        content = f.read()

    return filepath, content


def create_and_get_executive_report(
    data: list[CryptoCurrency], currency="usd", interval_minutes=60
):
    """
    Genera o reutiliza un reporte ejecutivo generado en PDF

    Returns:
        filename (str): Nombre del archivo generado o reutilizado.
        content (bytes): Contenido binario del archivo.
    """
    now = datetime.utcnow()
    report_hash = generate_report_hash(currency, now, interval_minutes, "pdf")
    filepath = get_cached_report_path(report_hash, suffix=".pdf")

    if os.path.exists(filepath):
        log.info(f"Usando reporte en caché: {filepath}")
    else:
        log.info(f"Generando nuevo reporte: {filepath}")

    df = crypto_data_to_df(data)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_path = temp_file.name

    save_bar_graph_as_image(df, temp_path)
    generate_executive_report(df, graph_path=temp_path, filename=filepath)

    # Eliminar el archivo temporal después de usarlo
    if os.path.exists(temp_path):
        os.remove(temp_path)

    with open(filepath, "rb") as f:
        content = f.read()

    return filepath, content
