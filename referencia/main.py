# main.py
from datetime import datetime
from dotenv import load_dotenv

# Importar funciones desde nuestros módulos
from modulos.data_handler import obtener_datos_cripto, procesar_datos
from modulos.visualizations import guardar_grafico_como_imagen
from modulos.report_generator import exportar_a_excel, generar_reporte_word, generar_reporte_pdf
from modulos.report_generator import enviar_correo_con_adjuntos
from modulos.utils import guardar_historico_reportes, limpiar_archivos_generados

# Cargar variables de entorno desde el archivo .env
load_dotenv()


def ejecutar_proceso_reportes():
    """Función principal que orquesta todo el proceso de generación de reportes."""
    print("--- INICIANDO PROCESO DE REPORTES DIARIOS ---")

    # --- CONFIGURACIÓN ---
    lista_distribucion = ["mail.com"]

    archivos_config = {
        "excel": "reporte_criptomonedas.xlsx",
        "word": "reporte_tendencias.docx",
        "pdf": "reporte_ejecutivo.pdf",
        "grafico": "variacion_criptos.png"
    }
    archivos_finales = [archivos_config["excel"],
                        archivos_config["word"], archivos_config["pdf"]]

    # --- 1. OBTENCIÓN Y PROCESAMIENTO DE DATOS ---
    datos_brutos = obtener_datos_cripto()
    if datos_brutos is None:
        print("--- PROCESO DETENIDO: No se pudieron obtener los datos. ---")
        return
    df_limpio = procesar_datos(datos_brutos)

    # --- 2. GENERACIÓN DE ENTREGABLES ---
    nombre_grafico_img = guardar_grafico_como_imagen(
        df_limpio, archivos_config["grafico"])
    exportar_a_excel(datos_brutos, df_limpio, archivos_config["excel"])
    generar_reporte_word(df_limpio, archivos_config["word"])
    if nombre_grafico_img:
        generar_reporte_pdf(df_limpio, nombre_grafico_img,
                            archivos_config["pdf"])

    # --- 3. PREPARACIÓN Y ENVÍO DE CORREO ---

    # Primero, generamos la tabla HTML
    tabla_html = df_limpio.to_html(index=False, classes='data-table', border=0)

    # Segundo, calculamos los valores para el resumen
    variacion_promedio = df_limpio['Variacion % (24h)'].mean()
    activo_ganador = df_limpio.loc[df_limpio['Variacion % (24h)'].idxmax()]
    activo_perdedor = df_limpio.loc[df_limpio['Variacion % (24h)'].idxmin()]

    # Tercero, creamos el diccionario COMPLETO
    datos_plantilla = {
        "{FECHA}": datetime.now().strftime("%d de %B de %Y"),
        "{VARIACION_PROMEDIO}": f"{variacion_promedio:.2f}",
        "{COLOR_TENDENCIA}": "#28a745" if variacion_promedio > 0 else "#dc3545",
        "{ACTIVO_GANADOR}": activo_ganador['Activo'],
        "{PORCENTAJE_GANADOR}": f"{activo_ganador['Variacion % (24h)']:.2f}",
        "{ACTIVO_PERDEDOR}": activo_perdedor['Activo'],
        "{PORCENTAJE_PERDEDOR}": f"{activo_perdedor['Variacion % (24h)']:.2f}",
        "{TABLA_DATOS_HTML}": tabla_html,
    }

    # Cuarto, llamamos a la función de envío
    if nombre_grafico_img:
        enviar_correo_con_adjuntos(
            lista_distribucion, archivos_finales, datos_plantilla, nombre_grafico_img)

    # --- 4. GESTIÓN DE ARCHIVOS ---
    guardar_historico_reportes(archivos_finales)
    # Limpiamos tanto los reportes como el gráfico temporal
    limpiar_archivos_generados(archivos_finales + [nombre_grafico_img])

    print("\n--- PROCESO DE REPORTES DIARIOS COMPLETADO EXITOSAMENTE ---")


if __name__ == "__main__":
    from datetime import datetime
    import time
    from threading import Thread
    from telegram_bot import bot

    # Para pruebas
    # ejecutar_proceso_reportes()

    # Tiempo Universal Coordinado (UTC)
    UTC_COLOMBIA = -5
    mensaje_enviado = False

    def run_bot():
        bot.infinity_polling()

    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # hora, minuto
    # para segundos agregar otro campo, modificar if y mensaje_enviado en el while
    enviar_cuando = (12, 0)

    try:
        print("\n--- PROCESO DE REPORTES DIARIOS INICIADO ---")

        print(f"Hora {11}:{59}:{55}")
        print(f"Hora {11}:{59}:{56}")
        print(f"Hora {11}:{59}:{57}")
        print(f"Hora {11}:{59}:{58}")
        print(f"Hora {11}:{59}:{59}")

        while True:
            utc_now = datetime.utcnow()
            hour = utc_now.hour + UTC_COLOMBIA
            minute = utc_now.minute
            second = utc_now.second

            minute = 0
            hour = 12
            # print(
            # f"Tiempo de ejecución: {hour:02d}:{minute:02d}:{second:02d}, enviado = {mensaje_enviado}")

            if hour == enviar_cuando[0] and minute == enviar_cuando[1] and not mensaje_enviado:
                mensaje_enviado = True
                print(
                    f"Enviando reporte diario a las {hour}:{minute}:{second}")
                ejecutar_proceso_reportes()

            mensaje_enviado = enviar_cuando[0] == hour and enviar_cuando[1] == minute
            time.sleep(1)
            break
    except KeyboardInterrupt:
        print("\nDeteniendo el bot...")
        bot.stop_polling()
        bot_thread.join()
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        bot.stop_polling()
        bot_thread.join()
    finally:
        bot.stop_polling()
        bot_thread.join()

    print(f"Hora {12}:00:01")
    print(f"Hora {12}:00:02")
    print(f"Hora {12}:00:03")
    print(f"Hora {12}:00:04")

    print("\n--- PROCESO FINALIZADO ---")
