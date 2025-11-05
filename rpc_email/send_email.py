import os
import logging
from datetime import datetime

import pandas as pd

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

from utils import ProjectEnv
from models import CryptoCurrency

log = logging.getLogger(__name__)


def crypto_data_to_df(data: list[CryptoCurrency]) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame([CryptoCurrency.to_dict(c) for c in data])
    df = df[["name", "current_price", "price_change_percentage_24h"]]

    return df


def _report(data):
    # Primero, generamos la tabla HTML
    df = crypto_data_to_df(data)
    html_table = df.to_html(index=False, classes="data-table", border=0)

    # Segundo, calculamos los valores para el resumen
    average = df["price_change_percentage_24h"].mean()
    max_coin = df.loc[df["price_change_percentage_24h"].idxmax()]
    min_coin = df.loc[df["price_change_percentage_24h"].idxmin()]

    # Tercero, creamos el diccionario COMPLETO
    data = {
        "{FECHA}": datetime.now().strftime("%d de %B de %Y"),
        "{VARIACION_PROMEDIO}": f"{average:.2f}",
        "{COLOR_TENDENCIA}": "#28a745" if average > 0 else "#dc3545",
        "{ACTIVO_GANADOR}": max_coin["name"],
        "{PORCENTAJE_GANADOR}": f"{max_coin['price_change_percentage_24h']:.2f}",
        "{ACTIVO_PERDEDOR}": min_coin["name"],
        "{PORCENTAJE_PERDEDOR}": f"{min_coin['price_change_percentage_24h']:.2f}",
        "{TABLA_DATOS_HTML}": html_table,
    }

    return data


def send_email(
    users: list[str], files: list[str], data: list[CryptoCurrency], graph_path: str
) -> None:
    """
    Envía un correo HTML con un gráfico y tabla embebidos, además de los archivos adjuntos.
    """

    df = _report(data)

    smtp_server = ProjectEnv.RPC_EMAIL_STMP_SERVER
    smtp_port = ProjectEnv.RPC_EMAIL_STMP_PORT
    email_user = ProjectEnv.RPC_EMAIL_USER
    email_password = ProjectEnv.RPC_EMAIL_PASSWORD

    # --- Creación del Mensaje ---
    # El contenedor principal es 'mixed' para combinar contenido y adjuntos.
    msg = MIMEMultipart("mixed")
    msg["From"] = email_user
    msg["To"] = ", ".join(users)
    msg["Subject"] = f"Reporte de Mercado de Criptomonedas - {df['{FECHA}']}"

    # Contenedor 'related' para el cuerpo HTML y la imagen embebida.
    msg_related = MIMEMultipart("related")

    # --- Cuerpo del Correo (HTML) ---
    try:
        template_path = os.path.join(os.path.dirname(__file__), "plantilla.html")

        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        for key, value in df.items():
            html = html.replace(key, str(value))

        # Adjuntar el HTML al contenedor 'related'
        msg_alternative = MIMEMultipart("alternative")
        msg_alternative.attach(MIMEText(html, "html"))
        msg_related.attach(msg_alternative)
    except FileNotFoundError:
        log.error("Error: No se encontró 'plantilla.html'.")
        return

    # --- Embeber el Gráfico ---
    try:
        with open(graph_path, "rb") as f_img:
            img = MIMEImage(f_img.read())

            # El 'Content-ID' debe coincidir con el 'cid:' en el HTML
            img.add_header("Content-ID", "<grafico_variacion>")
            msg_related.attach(img)
    except FileNotFoundError:
        log.error(f"Error: No se encontró el gráfico '{graph_path}'.")

    # Adjuntar el contenedor 'related' (HTML + imagen) al mensaje principal
    msg.attach(msg_related)

    # --- Adjuntar Archivos (Excel, Word, PDF) ---
    for f in files:
        try:
            with open(f, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=os.path.basename(f))
                part["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(f)}"'
                )
                msg.attach(part)
        except FileNotFoundError:
            log.error(f"Error: No se encontró el adjunto '{f}'.")

    # --- Envío del Correo ---
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, users, msg.as_string())

        log.info("Correo enviado correctamente.")
    except Exception as e:
        log.error(f"Error al enviar el correo: {e}")
    finally:
        if "server" in locals():
            server.quit()
