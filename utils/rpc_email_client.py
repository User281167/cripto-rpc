import sys
import os
import grpc
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generated import email_pb2, email_pb2_grpc
from .env import ProjectEnv

load_dotenv()


class RpcEmailClient:
    def __init__(self, async_mode=False):
        """
        Args:
            async_mode (bool): Comunicación asíncrona o sincrona.
                Defaults to False.
                TRUE: Asíncrono se debe usar async en cada función ya que se devuelve una coroutine.
        """
        if async_mode:
            self.channel = grpc.aio.insecure_channel(ProjectEnv.RPC_EMAIL)
        else:
            self.channel = grpc.insecure_channel(ProjectEnv.RPC_EMAIL)

        self.stub = email_pb2_grpc.EmailServiceStub(self.channel)

    def subscribe_email(self, email: str, hour: int, minute: int) -> email_pb2.SubscribeEmailResponse:
        request = email_pb2.SubscribeEmailRequest(email=email, hour=hour, minute=minute)
        return self.stub.SubscribeEmail(request)

    def unsubscribe_email(self, email: str) -> email_pb2.SubscribeEmailResponse:
        request = email_pb2.UnsubscribeEmailRequest(email=email)
        return self.stub.UnsubscribeEmail(request)
