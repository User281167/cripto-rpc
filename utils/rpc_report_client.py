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
    def __init__(self, async_mode=False):
        if async_mode:
            self.channel = grpc.aio.insecure_channel(ProjectEnv.RPC_REPORT)
        else:
            self.channel = grpc.insecure_channel(ProjectEnv.RPC_REPORT)

        self.stub = report_pb2_grpc.CryptoReportServiceStub(self.channel)

    def generate_crypto_report(self, currency: str = "usd") -> report_pb2.Report:
        request = report_pb2.ReportRequest(currency=currency)
        return self.stub.GenerateCryptoReport(request)

    def generate_trend_report(self, currency: str = "usd") -> report_pb2.Report:
        request = report_pb2.ReportRequest(currency=currency)
        return self.stub.GenerateTrendReport(request)

    def generate_executive_report(self, currency: str = "usd") -> report_pb2.Report:
        request = report_pb2.ReportRequest(currency=currency)
        return self.stub.GenerateExecutiveReport(request)

    def generate_bar_graph(self, currency: str = "usd") -> report_pb2.Report:
        request = report_pb2.ReportRequest(currency=currency)
        return self.stub.GenerateBarGraph(request)
