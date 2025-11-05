import os
import logging
import pandas as pd
from fpdf import FPDF

log = logging.getLogger(__name__)


class PDF(FPDF):
    def header(self):
        # Este método se deja vacío para tener control total sobre la portada y las páginas de contenido.
        pass

    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        # Fuente Arial itálica 8
        self.set_font("Helvetica", "I", 8)
        # Número de página
        self.cell(0, 10, "Página " + str(self.page_no()), 0, 0, "C")


def generate_executive_report(
    df: pd.DataFrame, graph_path: str, filename="executive_report.pdf"
):
    """
    Genera un reporte ejecutivo en PDF con portada, resumen y gráfico.

    Args:
        df (pd.DataFrame): El DataFrame con los datos limpios y calculados.
        graph_path (str): La ruta del gráfico generado.
        filename (str): El nombre del archivo PDF a generar.
    """
    if df is None:
        log.info("No hay datos para generar el reporte ejecutivo en PDF.")
        return

    try:
        # --- 1. Análisis para el Mini-Resumen ---
        activo_mayor_ganancia = df.loc[df["price_change_percentage_24h"].idxmax()]
        activo_mayor_perdida = df.loc[df["price_change_percentage_24h"].idxmin()]
        variacion_promedio = df["price_change_percentage_24h"].mean()

        # --- 2. Creación del PDF ---
        pdf = PDF()  # Asumiendo que tienes la clase PDF definida

        # --- Portada ---
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 24)
        pdf.cell(0, 80, "", ln=True)
        pdf.cell(0, 10, "Reporte Ejecutivo", ln=True, align="C")

        # --- Página de Contenido ---
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 15, "Resumen para la Gerencia", ln=True)

        # --- Resumen ---
        pdf.set_font("Helvetica", "", 11)
        resumen_texto = (
            f"El análisis de las últimas 24 horas muestra una tendencia general de mercado con una variación promedio de {variacion_promedio:.2f}%. "
            f"El activo con mejor desempeño fue {activo_mayor_ganancia['name']}, registrando un alza de {activo_mayor_ganancia['price_change_percentage_24h']:.2f}%. "
            f"En contraste, {activo_mayor_perdida['name']} fue el activo con la mayor caída, disminuyendo un {activo_mayor_perdida['price_change_percentage_24h']:.2f}%. "
            "Se recomienda monitorear la volatilidad y los activos destacados."
        )
        pdf.multi_cell(0, 6, resumen_texto)

        if graph_path and os.path.exists(graph_path):
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 15, "Rendimiento de Activos (Últimas 24h)", ln=True)

            pdf.image(graph_path, x=15, w=180)

        # --- 3. Guardar el PDF ---
        pdf.output(filename)
        log.info(f"Reporte ejecutivo generado en PDF: '{filename}'")
    except Exception as e:
        log.error(f"Error al generar el reporte ejecutivo en PDF: {e}")
