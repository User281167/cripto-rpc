import os
import sys
import grpc
import logging
import asyncio
import re
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import ProjectEnv, RpcInfoClient, RpcReportClient
from generated import email_pb2, email_pb2_grpc
from models import CryptoCurrency
from send_email import send_email


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)


class EmailService(email_pb2_grpc.EmailServiceServicer):
    def __init__(self):
        self.emails = []
        self.email_queue = asyncio.Queue()

    async def SubscribeEmail(self, request, context):
        log.info(f"Guardando correo electrónico \n{request}")

        email = request.email
        hour = request.hour
        minute = request.minute

        if not request.email:
            return email_pb2.SubscribeEmailResponse(
                success=False, message="No se ha proporcionado un correo electronico."
            )
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return email_pb2.SubscribeEmailResponse(
                success=False, message="El correo electronico no es valido."
            )
        elif hour is None or minute is None:
            return email_pb2.SubscribeEmailResponse(
                success=False, message="No se ha proporcionado una hora."
            )
        elif hour < 0 or hour > 23:
            return email_pb2.SubscribeEmailResponse(
                success=False, message="La hora debe estar entre 0 y 23."
            )
        elif minute < 0 or minute > 59:
            return email_pb2.SubscribeEmailResponse(
                success=False, message="Los minutos deben estar entre 0 y 59."
            )

        email = email.lower()

        if email not in self.emails:
            self.emails.append({"email": email, "hour": hour, "minute": minute})
            log.info(f"Correo electrónico guardado: {email}")

        return email_pb2.SubscribeEmailResponse(
            success=True, message="Correo electrónico guardado."
        )

    async def UnsubscribeEmail(self, request, context):
        log.info(f"Eliminando correo electrónico {request}")

        email = request.email

        if email in self.emails:
            self.emails.remove(email)
            log.info(f"Correo electrónico eliminado: {email}")

        return email_pb2.SubscribeEmailResponse(
            success=True, message="Correo electrónico eliminado."
        )

    def _filter_emails(self):
        """
        Cada minuto filtrar los emails para saber cuales serán enviados
        """

        now = datetime.utcnow()
        hour = now.hour
        minute = now.minute

        log.info(f"Tiempo de ejecución: {hour:02d}:{minute:02d}")

        emails_to_send = [
            email
            for email in self.emails
            if email["hour"] == hour and email["minute"] == minute
        ]

        return emails_to_send

    async def _process_emails(self, emails_to_send):
        """
        Procesar emails
        Obtener reportes y adjuntarlos en el mensaje
        """

        if not emails_to_send:
            return

        users = [email["email"] for email in emails_to_send]
        log.info(f"Enviando correo electrónico {users}")

        report = RpcReportClient()
        info_task = RpcInfoClient().get_top_cryptos()
        png_task = report.generate_bar_graph()
        excel_task = report.generate_crypto_report()
        word_task = report.generate_trend_report()
        pdf_task = report.generate_executive_report()

        log.info("Esperando información de las tareas...")

        info_result, png_result, excel_result, word_result, pdf_result = (
            await asyncio.gather(info_task, png_task, excel_task, word_task, pdf_task)
        )

        info = [CryptoCurrency.from_proto(c) for c in info_result.cryptos]
        reports = [png_result, excel_result, word_result, pdf_result]

        output_folder = ".temp"

        # Ruta completa del archivo
        os.makedirs(output_folder, exist_ok=True)

        for report in reports:
            filename = report.filename
            content = report.content

            filepath = os.path.join(output_folder, filename)

            # Guardar el contenido binario como archivo
            with open(filepath, "wb") as f:
                f.write(content)

        graph_path = os.path.join(output_folder, reports[0].filename)

        send_email(
            users=users,
            files=[os.path.join(output_folder, r.filename) for r in reports],
            data=info,
            graph_path=graph_path,
        )

        # Eliminar los archivos temporales
        for report in reports:
            filepath = os.path.join(output_folder, report.filename)
            os.remove(filepath)

    async def email_collector(self):
        """
        Cada minuto filtrar los emails para saber cuales serán enviados
        Guardar en cola
        """

        last_processed_minute = None

        while True:
            emails_to_send = self._filter_emails()
            current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")

            if current_minute != last_processed_minute:
                log.info(f"Procesando emails para {current_minute}")

                last_processed_minute = current_minute
                emails_to_send = self._filter_emails()
                log.info(f"Encontrados {len(emails_to_send)} emails para enviar.")

                if emails_to_send:
                    log.info("Guardando en cola...")
                    await self.email_queue.put(emails_to_send)
            await asyncio.sleep(10)

    async def email_worker(self):
        """
        Procesar emails en la cola de envíos
        """
        while True:
            try:
                log.info("Esperando tarea de email...")
                emails_to_send = await self.email_queue.get()

                log.info("Procesando tarea de email...")
                await self._process_emails(emails_to_send)

                self.email_queue.task_done()
                log.info("Tarea de email finalizada.")
            except Exception as e:
                log.error(f"Error procesando email: {e}")
            finally:
                await asyncio.sleep(10)


async def serve():
    log.info("Iniciando el servidor...")

    # Comenzar servidor gRPC
    server = grpc.aio.server()
    email_service = EmailService()
    email_pb2_grpc.add_EmailServiceServicer_to_server(email_service, server)

    server.add_insecure_port(ProjectEnv.RPC_EMAIL)
    await server.start()

    # Lanzar recolector y worker en paralelo
    task_worker = asyncio.create_task(email_service.email_collector())
    email_worker = asyncio.create_task(email_service.email_worker())

    log.info("Servidor iniciado.")

    try:
        await server.wait_for_termination()
    finally:
        log.info("Ctrl+C detectado. Cerrando servidor...")
        task_worker.cancel()
        email_worker.cancel()
        await server.stop(grace=None)


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("Servidor detenido manualmente.")
