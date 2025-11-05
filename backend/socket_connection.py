"""
Socket para enviar información de broadcast o multicast
"""

import socketio
import logging
import asyncio

from models import CryptoCurrency, CryptoHistoryItem

log = logging.getLogger(__name__)


class SocketConnection:
    def __init__(self, rpc_client):
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
        )
        self.rpc = rpc_client
        self.active_rooms = {}

        @self.sio.event
        async def connect(sid, environ):
            log.info(f"Connected: {sid}")

        @self.sio.event
        async def disconnect(sid):
            log.info(f"Disconnected: {sid}")

        @self.sio.event
        async def join_room(sid, data):
            """
            Crear o unirse a una sala para hacer multicast de criptomonedas

            sid: Id de la sesión
            data: Diccionario con la clave "room" que contiene el nombre de la sala
            """

            try:
                room = data["room"]
                await self.sio.enter_room(sid, room)

                # Inicializar si no existe
                if room not in self.active_rooms:
                    self.active_rooms[room] = 0

                self.active_rooms[room] += 1
                log.info(f"{sid} se unió a la sala {room}")
            except Exception as e:
                log.error(f"Error al unirse a la sala: {e}")

        @self.sio.event
        async def leave_room(sid, data):
            try:
                room = data["room"]
                await self.sio.leave_room(sid, room)

                if room in self.active_rooms:
                    self.active_rooms[room] = max(0, self.active_rooms[room] - 1)

                log.info(f"{sid} salió de la sala {room}")
            except Exception as e:
                log.error(f"Error al salir de la sala: {e}")

    async def poll_crypto_rooms(self, rpc_client):
        """Polling de salas activas cada 5 segundos"""
        try:
            log.info("Iniciando polling de salas...")

            while True:
                for room in list(self.active_rooms.keys()):
                    if self.active_rooms[room] > 0:
                        try:
                            # Obtener datos históricos
                            response = await rpc_client.get_price_history(id=room)

                            data = [
                                CryptoHistoryItem.from_json(h).to_dict()
                                for h in response.history
                            ]

                            await self.sio.emit("update", {"data": data}, room=room)

                            log.info(
                                f"Enviado update a sala '{room}' ({len(data)} items)"
                            )
                        except Exception as e:
                            log.error(f"Error polling sala {room}: {e}")

                await asyncio.sleep(10)  # polling

        except asyncio.CancelledError:
            log.info("Polling cancelado")
            raise
        except Exception as e:
            log.error(f"Error en poll_crypto_rooms: {e}")

    async def stream_and_broadcast(self):
        """
        Stream de las criptomonedas más importantes y emite dos eventos broadcast
        """
        try:
            log.info("Iniciando stream de criptomonedas...")
            stream = await self.rpc.stream_top_cryptos(quantity=50)

            async for update in stream:
                cryptos = [
                    CryptoCurrency.from_proto(c).to_dict() for c in update.cryptos
                ]

                log.info(f"Broadcasting {len(cryptos)} cryptos")

                # Emitir los 50 a quienes lo necesiten
                # Emitir los 5 primeros como resumen
                await asyncio.gather(
                    self.sio.emit("top50_update", {"cryptos": cryptos}),
                    self.sio.emit("top5_update", {"cryptos": cryptos[:5]}),
                )

        except asyncio.CancelledError:
            log.info("Stream cancelado")
            raise
        except Exception as e:
            log.error(f"Error en stream_and_broadcast: {e}")
