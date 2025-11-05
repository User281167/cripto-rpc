import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import RpcReportClient


def main():
    rpc = RpcReportClient()

    print("Esperando resultados...")
    res = rpc.generate_executive_report()
    filename = res.filename
    content = res.content

    output_folder = ".temp"

    # Ruta completa del archivo
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, filename)

    # Guardar el contenido binario como archivo
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"Reporte guardado en: {filepath}")


if __name__ == "__main__":
    main()
