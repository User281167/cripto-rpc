import pandas as pd
import logging

from models import CryptoCurrency

log = logging.getLogger(__name__)


def generate_crypto_report(
    data: list[CryptoCurrency],
    data_frame: pd.DataFrame,
    filename="crypto_report.xlsx",
):
    """
    Exporta los datos crudos y procesados a un archivo de Excel con dos hojas.

    Args:
        data (list): La lista de diccionarios con los datos originales de la API.
        data_frame (pd.DataFrame): El DataFrame con los datos limpios y calculados.
        filename (str): El nombre del archivo Excel a generar.
    """
    if not data or data_frame is None:
        log.info("There is no data to export to Excel.")
        return

    try:
        df = pd.DataFrame(data)

        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            # Hoja 1: Datos Crudos
            df.to_excel(writer, sheet_name="Datos Crudos", index=False)

            # Hoja 2: Cálculos y Datos Limpios
            data_frame.to_excel(writer, sheet_name="Cálculos", index=False)

        log.info(f"Reporte generado exitosamente en '{filename}'")
    except Exception as e:
        log.error(f"Error al generar reporte en Excel: {e}")
