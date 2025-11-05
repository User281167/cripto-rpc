import os
import sys
import grpc
import logging
import asyncio
from concurrent import futures

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import RpcInfoClient, ProjectEnv
from generated import report_pb2, report_pb2_grpc
from models import CryptoCurrency

from report import (
    create_and_get_crypto_report,
    create_and_get_trend_report,
    create_and_get_executive_report,
    create_and_get_bar_graph,
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)


class CryptoReportService(report_pb2_grpc.CryptoReportServiceServicer):
    def _get_data(self, request, context, quantity: int = 50):
        log.info(f"Obteniendo datos de criptomonedas {request}")

        data = None

        try:
            data = RpcInfoClient().get_top_cryptos(request.currency, quantity)
            data = [CryptoCurrency.from_proto(c) for c in data.cryptos]
        except Exception as e:
            log.error(f"Error al obtener datos de criptomonedas: \n{e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al obtener los datos de criptomonedas.")
            return report_pb2.Report()

        return data

    async def GenerateCryptoReport(self, request, context):
        log.info(f"Obteniendo reporte de criptomonedas {request}")
        data = self._get_data(request, context)

        if not data:
            return report_pb2.Report()

        try:
            filename, content = create_and_get_crypto_report(data, request.currency)

            return report_pb2.Report(
                filename=os.path.basename(filename), content=content
            )
        except Exception as e:
            log.error(f"Error al generar el reporte: \n{e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al generar el reporte.")
            return report_pb2.Report()

    async def GenerateTrendReport(self, request, context):
        log.info(f"Obteniendo reporte de tendencias {request}")
        data = self._get_data(request, context)

        if not data:
            return report_pb2.Report()

        try:
            filename, content = create_and_get_trend_report(data, request.currency)

            return report_pb2.Report(
                filename=os.path.basename(filename), content=content
            )
        except Exception as e:
            log.error(f"Error al generar el reporte de tendencias: \n{e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al generar el reporte de tendencias.")
            return report_pb2.Report()

    async def GenerateExecutiveReport(self, request, context):
        log.info(f"Obteniendo reporte ejecutivo {request}")
        data = self._get_data(request, context, quantity=15)

        if not data:
            return report_pb2.Report()

        try:
            filename, content = create_and_get_executive_report(data, request.currency)

            return report_pb2.Report(
                filename=os.path.basename(filename), content=content
            )
        except Exception as e:
            log.error(f"Error al generar el reporte ejecutivo: \n{e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al generar el reporte ejecutivo.")
            return report_pb2.Report()

    async def GenerateBarGraph(self, request, context):
        log.info(f"Obteniendo gráfico de barras {request}")
        data = self._get_data(request, context, quantity=15)

        if not data:
            return report_pb2.Report()

        try:
            filename, content = create_and_get_bar_graph(data, request.currency)

            return report_pb2.Report(
                filename=os.path.basename(filename), content=content
            )
        except Exception as e:
            log.error(f"Error al generar el gráfico de barras: \n{e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al generar el gráfico de barras.")
            return report_pb2.Report()


async def serve():
    log.info("Iniciando el servidor de reportes...")

    # Comenzar servidor gRPC
    server = grpc.aio.server()
    report_pb2_grpc.add_CryptoReportServiceServicer_to_server(
        CryptoReportService(), server
    )

    server.add_insecure_port(ProjectEnv.RPC_REPORT)
    await server.start()

    log.info("Servidor iniciado.")

    try:
        await server.wait_for_termination()
    finally:
        log.info("Ctrl+C detectado. Cerrando servidor...")
        await server.stop(grace=None)
        print("\n--- PROCESO FINALIZADO ---")


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("Servidor detenido manualmente.")
