import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from socketio import ASGIApp

from contextlib import asynccontextmanager
import asyncio
import logging

from utils import ProjectEnv, RpcInfoClient
from socket_connection import SocketConnection

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)

# Configuración de Redis (None para dev, URL para producción)
REDIS_URL = ProjectEnv.SOCKET_REDIS_URL  # export REDIS_URL=redis://localhost:6379

rpc_client = RpcInfoClient(async_mode=True)
socket_conn = SocketConnection(rpc_client, redis_url=REDIS_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup: Iniciar tareas en background
    log.info("Iniciando servidor Socket.IO...")

    stream_task = asyncio.create_task(socket_conn.stream_and_broadcast())
    poll_task = asyncio.create_task(socket_conn.poll_crypto_rooms())

    log.info("Tareas de Socket.IO iniciadas")

    yield  # Ejecutando las tareas en background

    # Shutdown: Cancelar tareas
    log.info("Deteniendo servidor...")
    stream_task.cancel()
    poll_task.cancel()

    try:
        await stream_task
        await poll_task
    except asyncio.CancelledError:
        log.info("Tareas canceladas correctamente")


app = FastAPI(
    title="Crypto Socket.IO Service",
    description="Servicio de WebSocket para actualizaciones en tiempo real",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ProjectEnv.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar Socket.IO en la raíz
socket_app = ASGIApp(socket_conn.sio)
app.mount("/", socket_app)


if __name__ == "__main__":
    import uvicorn

    port = int(ProjectEnv.SOCKET_BACKEND_PORT)

    log.info(f"Servidor escuchando en {ProjectEnv.BACKEND_HOST}:{port}")

    if REDIS_URL:
        log.info(f"Modo PRODUCCIÓN con Redis: {REDIS_URL}")
    else:
        log.info("Modo DESARROLLO (sin Redis)")

    uvicorn.run(
        "main:app",
        host=ProjectEnv.BACKEND_HOST,
        port=port,
        reload=not REDIS_URL,  # Auto-reload solo en dev
    )
