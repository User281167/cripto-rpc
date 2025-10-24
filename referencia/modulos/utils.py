# modulos/utils.py
import os
import shutil
from datetime import datetime


def guardar_historico_reportes(
    archivos_a_archivar, directorio_historico="historial_reportes"
):
    """Guarda una copia de los reportes en una subcarpeta diaria."""
    fecha_actual_str = datetime.now().strftime("%Y-%m-%d")
    directorio_diario = os.path.join(directorio_historico, fecha_actual_str)
    os.makedirs(directorio_diario, exist_ok=True)

    print(f"\n📦 Guardando histórico de reportes en '{directorio_diario}'...")
    for archivo_original_path in archivos_a_archivar:
        if os.path.exists(archivo_original_path):
            try:
                shutil.copy(
                    archivo_original_path,
                    os.path.join(
                        directorio_diario, os.path.basename(archivo_original_path)
                    ),
                )
                print(f"   - '{os.path.basename(archivo_original_path)}' archivado.")
            except Exception as e:
                print(f"❌ Error al archivar '{archivo_original_path}': {e}")


def limpiar_archivos_generados(lista_archivos):
    """Elimina los archivos generados de la carpeta de trabajo."""
    print("\n🧹 Limpiando archivos de trabajo...")
    for archivo in lista_archivos:
        if archivo and os.path.exists(archivo):
            os.remove(archivo)
            print(f"   - Archivo '{archivo}' eliminado.")
