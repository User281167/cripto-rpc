import sys
import os
import grpc
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generated import report_pb2, report_pb2_grpc
from utils import ProjectEnv

load_dotenv()


class RpcReportClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(ProjectEnv.RPC_REPORT)
        self.stub = report_pb2_grpc.CryptoReportServiceStub(self.channel)

    async def generate_crypto_report(self, currency: str = "usd") -> report_pb2.Report:
        request = report_pb2.ReportRequest(currency=currency)
        return self.stub.GenerateCryptoReport(request)
