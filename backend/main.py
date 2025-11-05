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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Iniciar tareas en background
    stream_task = asyncio.create_task(socket_conn.stream_and_broadcast())
    poll_task = asyncio.create_task(socket_conn.poll_crypto_rooms())

    log.info("Tareas de Socket.IO iniciadas")

    yield  # Ejecución asíncrona

    # Cancelar tareas
    stream_task.cancel()
    poll_task.cancel()

    try:
        await stream_task
        await poll_task
    except asyncio.CancelledError:
        log.info("Tareas canceladas correctamente")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ProjectEnv.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rpc_client = RpcInfoClient(async_mode=True)
socket_conn = SocketConnection(rpc_client)
stream_task = None

# Montar WebSocket en ruta /
socket_app = ASGIApp(socket_conn.sio)
app.mount("/", socket_app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=ProjectEnv.BACKEND_HOST, port=ProjectEnv.BACKEND_PORT)
