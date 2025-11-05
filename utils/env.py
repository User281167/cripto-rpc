import os
from dotenv import load_dotenv

load_dotenv()


class ProjectEnv:
    RPC_INFO = os.getenv("RPC_INFO", "127.0.0.1:50051")
    RPC_INFO_REDIS_HOST = os.getenv("RPC_INFO_REDIS_HOST", "127.0.0.1")
    RPC_INFO_REDIS_PORT = os.getenv("RPC_INFO_REDIS_PORT", 6380)

    RPC_REPORT = os.getenv("RPC_REPORT", "127.0.0.1:50052")
