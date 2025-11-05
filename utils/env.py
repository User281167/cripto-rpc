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

    SOCKET_SERVER_URL = os.getenv("SOCKET_SERVER_URL", "http://127.0.0.1:50054")
    BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT = os.getenv("BACKEND_PORT", 8000)

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
