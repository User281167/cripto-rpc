import os
from dotenv import load_dotenv

load_dotenv()


class ProjectEnv:
    RPC_INFO = os.getenv("RPC_INFO", "127.0.0.1:50051")
    RPC_INFO_REDIS_HOST = os.getenv("RPC_INFO_REDIS_HOST", "127.0.0.1")
    RPC_INFO_REDIS_PORT = os.getenv("RPC_INFO_REDIS_PORT", 6380)

    RPC_REPORT = os.getenv("RPC_REPORT", "127.0.0.1:50052")

    RPC_EMAIL = os.getenv("RPC_EMAIL", "127.0.0.1:50053")
    RPC_EMAIL_STMP_SERVER = os.getenv("RPC_EMAIL_STMP_SERVER", "smtp.gmail.com")
    RPC_EMAIL_STMP_PORT = os.getenv("RPC_EMAIL_STMP_PORT", 587)
    RPC_EMAIL_USER = os.getenv("RPC_EMAIL_USER", "user")
    RPC_EMAIL_PASSWORD = os.getenv("RPC_EMAIL_PASSWORD", "password")
