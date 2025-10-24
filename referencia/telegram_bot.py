import telebot
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Nuevas importaciones para los botones interactivos
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Cargar variables de entorno ---
load_dotenv(dotenv_path=".env")

# --- CONFIGURACIÓN DEL BOT Y CONSTANTES ---
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError(
        "No se encontró el token del bot. Por favor, configúralo en la variable de entorno TELEGRAM_TOKEN."
    )

bot = telebot.TeleBot(BOT_TOKEN)

# Definimos constantes para las rutas, facilitando el mantenimiento
DIRECTORIO_HISTORICO = "historial_reportes"
NOMBRE_PDF_REPORTE = "reporte_ejecutivo.pdf"


# ===================================================================
# FUNCIONES AUXILIARES PARA OBTENER DATOS (EN TIEMPO REAL)
# ===================================================================


def obtener_datos_cripto(coin_id):
    """Obtiene el precio actual y la variación de 24h de una criptomoneda específica."""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[coin_id]["usd"], data[coin_id]["usd_24h_change"]
    except Exception as e:
        print(f"Error al obtener datos de {coin_id}: {e}")
        return None, None


def obtener_cotizacion_divisas():
    """Obtiene las tasas de cambio de divisas principales usando las tasas de CoinGecko."""
    try:
        url = "https://api.coingecko.com/api/v3/exchange_rates"
        response = requests.get(url)
        response.raise_for_status()
        rates = response.json()["rates"]
        tasa_eur_usd = rates["usd"]["value"] / rates["eur"]["value"]
        return tasa_eur_usd
    except Exception as e:
        print(f"Error al obtener tasas de cambio: {e}")
        return None


# --- NUEVA FUNCIÓN PARA EL RESUMEN ---
def obtener_datos_resumen():
    """Obtiene los datos de BTC, Dólar (Tether) y Euro de forma eficiente."""
    try:
        # 1. Obtener datos de criptos en una sola llamada
        ids = "bitcoin,tether"
        url_cripto = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
        response_cripto = requests.get(url_cripto)
        response_cripto.raise_for_status()
        data_cripto = response_cripto.json()

        # 2. Obtener tasa del Euro
        tasa_euro = obtener_cotizacion_divisas()

        # 3. Empaquetar los resultados
        resultado = {
            "bitcoin": data_cripto.get("bitcoin"),
            "dolar": data_cripto.get("tether"),
            "euro": tasa_euro,
        }
        return resultado
    except Exception as e:
        print(f"Error al obtener los datos para el resumen: {e}")
        return None


# --- NUEVA FUNCIÓN DE UTILIDAD ---
def formatear_cambio(variacion):
    """Convierte el % de variación en un texto descriptivo."""
    if variacion is None:
        return "sin datos"

    # Umbral para considerar un cambio como "estable"
    umbral_estabilidad = 0.5

    if variacion > umbral_estabilidad:
        return f"subió un *{variacion:.2f}%* 📈"
    elif variacion < -umbral_estabilidad:
        # Usamos abs() para mostrar el número como positivo en la frase "bajó un X%"
        return f"bajó un *{abs(variacion):.2f}%* 📉"
    else:
        return "se mantiene *estable* ➖"


# ===================================================================
# MANEJADORES DE COMANDOS DEL BOT
# ===================================================================
@bot.message_handler(commands=["start", "help", "ayuda"])
def send_welcome(message):
    """Mensaje de bienvenida y ayuda actualizado."""
    texto_ayuda = (
        "¡Bienvenido al Bot de Reportes de Gerencia!\n\n"
        "Comandos disponibles:\n\n"
        "📄 *Reportes:*\n"
        "    `/reporte` - Envía el reporte PDF generado *hoy*.\n"
        "    `/historial` - Muestra una lista de fechas para descargar reportes anteriores.\n\n"
        "📊 *Consultas Rápidas:*\n"
        "    `/resumen` - Un vistazo general del mercado.\n"
        "    `/dolar`, `/euro`, `/bitcoin` - Cotizaciones individuales."
    )
    bot.reply_to(message, texto_ayuda, parse_mode="Markdown")


# --- REQUERIMIENTO 1: MANEJADOR /reporte MODIFICADO ---
@bot.message_handler(commands=["reporte"])
def enviar_reporte_actual(message):
    """Busca el PDF en la carpeta de la fecha actual y lo envía."""
    bot.send_chat_action(message.chat.id, "upload_document")

    fecha_actual_str = datetime.now().strftime("%Y-%m-%d")
    ruta_pdf_actual = os.path.join(
        DIRECTORIO_HISTORICO, fecha_actual_str, NOMBRE_PDF_REPORTE
    )

    try:
        with open(ruta_pdf_actual, "rb") as doc:
            bot.send_document(
                message.chat.id,
                doc,
                caption=f"Aquí está el reporte ejecutivo del día de hoy ({fecha_actual_str}).",
            )
    except FileNotFoundError:
        bot.reply_to(
            message,
            f"❌ Lo siento, el reporte del día de hoy ({fecha_actual_str}) aún no ha sido generado o no se encuentra.",
        )
    except Exception as e:
        bot.reply_to(message, f" Ocurrió un error inesperado al enviar el reporte: {e}")


# --- REQUERIMIENTO 2: NUEVA FUNCIÓN /historial ---
@bot.message_handler(commands=["historial"])
def mostrar_historial(message):
    """Escanea el directorio de historiales y muestra las fechas como botones."""
    bot.send_chat_action(message.chat.id, "typing")

    try:
        # Listar todos los directorios (fechas) en la carpeta de historiales
        fechas_disponibles = [
            d
            for d in os.listdir(DIRECTORIO_HISTORICO)
            if os.path.isdir(os.path.join(DIRECTORIO_HISTORICO, d))
        ]

        if not fechas_disponibles:
            bot.reply_to(message, "No se encontraron reportes en el historial.")
            return

        # Ordenar las fechas de más reciente a más antigua
        fechas_disponibles.sort(reverse=True)

        # Crear el teclado de botones en línea
        markup = InlineKeyboardMarkup()
        markup.row_width = 2  # Puedes ajustar cuántos botones quieres por fila

        # Añadir un botón por cada fecha encontrada
        for fecha in fechas_disponibles:
            # El callback_data es la información que el bot recibe cuando se presiona el botón
            # Usamos un prefijo 'get_report_' para identificar la acción
            button = InlineKeyboardButton(fecha, callback_data=f"get_report_{fecha}")
            markup.add(button)

        bot.send_message(
            message.chat.id,
            "Por favor, seleccione la fecha del reporte que desea descargar:",
            reply_markup=markup,
        )

    except FileNotFoundError:
        bot.reply_to(
            message, f"El directorio de historiales '{DIRECTORIO_HISTORICO}' no existe."
        )
    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error al buscar el historial: {e}")


# --- REQUERIMIENTO 2 (Parte B): MANEJADOR PARA LOS BOTONES ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_report_"))
def callback_query_handler(call):
    """Manejador que se activa cuando un usuario presiona un botón de fecha."""

    # Extraer la fecha del callback_data (ej. de 'get_report_2023-10-27' extrae '2023-10-27')
    fecha_solicitada = call.data.split("_")[2]

    # Avisar al usuario que la acción fue recibida
    bot.answer_callback_query(call.id, f"Buscando reporte para {fecha_solicitada}...")

    # Editar el mensaje original para que el usuario sepa qué seleccionó
    bot.edit_message_text(
        f"Preparando el reporte del día *{fecha_solicitada}*...",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
    )

    ruta_pdf = os.path.join(DIRECTORIO_HISTORICO, fecha_solicitada, NOMBRE_PDF_REPORTE)

    try:
        with open(ruta_pdf, "rb") as doc:
            bot.send_document(
                call.message.chat.id,
                doc,
                caption=f"Reporte ejecutivo del {fecha_solicitada}.",
            )
    except FileNotFoundError:
        bot.send_message(
            call.message.chat.id,
            f"❌ No se pudo encontrar el archivo PDF para la fecha {fecha_solicitada}.",
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ocurrió un error inesperado: {e}")


@bot.message_handler(commands=["dolar", "usd"])
def enviar_dolar(message):
    bot.send_chat_action(message.chat.id, "typing")
    precio, variacion = obtener_datos_cripto("tether")
    if precio is not None:
        signo = "📈" if variacion >= 0 else "📉"
        respuesta = f"💵 *Cotización Dólar (USDT)*\n\nPrecio: *${precio:,.4f} USD*\nVariación (24h): *{variacion:.2f}%* {signo}"
        bot.reply_to(message, respuesta, parse_mode="Markdown")
    else:
        bot.reply_to(
            message,
            "❌ Lo siento, no pude obtener la cotización del dólar en este momento.",
        )


@bot.message_handler(commands=["euro", "eur"])
def enviar_euro(message):
    bot.send_chat_action(message.chat.id, "typing")
    tasa_eur_usd = obtener_cotizacion_divisas()
    if tasa_eur_usd is not None:
        respuesta = f"💶 *Cotización Euro vs Dólar*\n\n1 EUR equivale a *${tasa_eur_usd:,.2f} USD*"
        bot.reply_to(message, respuesta, parse_mode="Markdown")
    else:
        bot.reply_to(
            message,
            "❌ Lo siento, no pude obtener la cotización del euro en este momento.",
        )


@bot.message_handler(commands=["bitcoin", "btc"])
def enviar_bitcoin(message):
    bot.send_chat_action(message.chat.id, "typing")
    precio, variacion = obtener_datos_cripto("bitcoin")
    if precio is not None:
        signo = "📈" if variacion >= 0 else "📉"
        respuesta = f"₿ *Cotización Bitcoin (BTC)*\n\nPrecio: *${precio:,.2f} USD*\nVariación (24h): *{variacion:.2f}%* {signo}"
        bot.reply_to(message, respuesta, parse_mode="Markdown")
    else:
        bot.reply_to(
            message,
            "❌ Lo siento, no pude obtener la cotización de Bitcoin en este momento.",
        )


@bot.message_handler(commands=["reporte"])
def enviar_reporte(message):
    bot.send_chat_action(message.chat.id, "upload_document")
    try:
        with open(NOMBRE_PDF_REPORTE, "rb") as doc:
            bot.send_document(
                message.chat.id, doc, caption="Aquí está el último reporte ejecutivo."
            )
    except FileNotFoundError:
        bot.reply_to(
            message,
            f" Lo siento, el archivo '{NOMBRE_PDF_REPORTE}' no fue encontrado. Asegúrese de que el script principal se haya ejecutado para generarlo.",
        )
    except Exception as e:
        bot.reply_to(message, f" Ocurrió un error al intentar enviar el reporte: {e}")


@bot.message_handler(commands=["resumen"])
def enviar_resumen(message):
    bot.send_chat_action(message.chat.id, "typing")

    try:
        resumen = obtener_datos_resumen()
        bot.reply_to(message, resumen)
    except Exception as e:
        bot.reply_to(message, f"Ocurrio un error al obtener el resumen: {e}")
        return


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(
        message,
        "Comando no reconocido. Usa /help para ver la lista de comandos disponibles.",
    )


# ===================================================================
# INICIO DEL BOT
# ===================================================================
if __name__ == "__main__":
    print("🤖 Bot de Telegram iniciado...")
    print("Presiona CTRL+C para detenerlo.")
    bot.infinity_polling()
