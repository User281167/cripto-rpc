"""
Socket para enviar información de broadcast o multicast
Soporta modo dev (sin Redis) y producción (con Redis)
"""

import socketio
import logging
import asyncio
from typing import Optional

from models import CryptoCurrency, CryptoHistoryItem

log = logging.getLogger(__name__)


class SocketConnection:
    def __init__(self, rpc_client, redis_url: Optional[str] = None):
        """
        Inicializa Socket.IO con soporte opcional de Redis

        Args:
            rpc_client: Cliente RPC para obtener datos
            redis_url: URL de Redis (ej: 'redis://localhost:6379').
                      Si es None, funciona en modo single-instance (dev)
        """
        # Configurar client_manager según si tenemos Redis
        client_manager = None

        if redis_url:
            log.info(f"Configurando Redis adapter: {redis_url}")
            client_manager = socketio.AsyncRedisManager(redis_url)
        else:
            log.info("Modo dev: Sin Redis (single instance)")

        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            client_manager=client_manager,  # None en dev, Redis en producción
        )

        self.rpc = rpc_client
        self.active_rooms = {}
        self.cached_top5 = []
        self.cached_top50 = {}  # Cache por crypto_id

        @self.sio.event
        async def connect(sid, environ):
            log.info(f"Connected: {sid}")

            # Enviar datos cacheados inmediatamente
            if self.cached_top5:
                await self.sio.emit(
                    "top5_update", {"cryptos": self.cached_top5}, to=sid
                )
                log.info(f"Enviado top5 cacheado a {sid}")

        @self.sio.event
        async def disconnect(sid):
            log.info(f"Disconnected: {sid}")

        @self.sio.event
        async def subscribe_top50(sid):
            """Cliente se suscribe al top 50 (cuando está en /)"""
            await self.sio.enter_room(sid, "top50_subscribers")
            log.info(f"{sid} suscrito a top50")

            # Enviar datos cacheados inmediatamente
            if self.cached_top50:
                cryptos_list = list(self.cached_top50.values())[:50]
                await self.sio.emit("top50_update", {"cryptos": cryptos_list}, to=sid)
                log.info(f"Enviado top50 cacheado a {sid}")

        @self.sio.event
        async def unsubscribe_top50(sid):
            """Cliente se desuscribe del top 50 (cuando sale de /)"""
            await self.sio.leave_room(sid, "top50_subscribers")
            log.info(f"{sid} desuscrito de top50")

        @self.sio.event
        async def join_room(sid, data):
            """
            Unirse a una sala para recibir updates de una crypto específica
            """
            try:
                room = data["room"]
                await self.sio.enter_room(sid, room)

                # Inicializar contador si no existe
                if room not in self.active_rooms:
                    self.active_rooms[room] = 0

                self.active_rooms[room] += 1
                log.info(
                    f"{sid} se unió a la sala {room} (total: {self.active_rooms[room]})"
                )

                # Obtener historial real inmediatamente al unirse
                try:
                    response = await self.rpc.get_price_history(
                        id=room, history_size=50
                    )
                    data = [
                        CryptoHistoryItem.from_proto(response.id, h).to_dict()
                        for h in response.prices
                    ]
                    await self.sio.emit("crypto_update", {"data": data}, to=sid)
                    log.info(f"Enviado historial de {room} a {sid} ({len(data)} items)")
                except Exception as e:
                    log.error(f"Error obteniendo historial para {room}: {e}")
                    # Si falla, enviar array vacío para que el cliente sepa que está conectado
                    await self.sio.emit("crypto_update", {"data": []}, to=sid)

            except Exception as e:
                log.error(f"❌ Error al unirse a la sala: {e}")

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

    async def poll_crypto_rooms(self):
        """
        Polling de salas activas cada 10 segundos
        Obtiene historial de precios para cryptos con usuarios suscritos
        """
        try:
            log.info("Iniciando polling de salas...")

            while True:
                active_count = len([r for r in self.active_rooms.values() if r > 0])

                if active_count > 0:
                    log.info(f"Polling {active_count} salas activas")

                for room in list(self.active_rooms.keys()):
                    if self.active_rooms[room] <= 0:
                        del self.active_rooms[room]
                        continue

                    try:
                        response = await self.rpc.get_price_history(
                            id=room, history_size=50
                        )

                        data = [
                            CryptoHistoryItem.from_proto(response.id, h).to_dict()
                            for h in response.prices
                        ]

                        await self.sio.emit("crypto_update", {"data": data}, room=room)
                        log.info(f"crypto_update → sala '{room}' ({len(data)} items)")

                    except Exception as e:
                        log.error(f"Error polling sala {room}: {e}")

                await asyncio.sleep(10)

        except asyncio.CancelledError:
            log.info("Polling cancelado")
            raise
        except Exception as e:
            log.error(f"Error en poll_crypto_rooms: {e}")

    async def stream_and_broadcast(self):
        """
        Stream de las criptomonedas más importantes y emite dos eventos:
        - top5_update: broadcast a TODOS
        - top50_update: solo a suscritos en sala "top50_subscribers"
        """
        try:
            log.info("Iniciando stream de criptomonedas...")
            stream = self.rpc.stream_top_cryptos(quantity=50)

            async for update in stream:
                cryptos = [
                    CryptoCurrency.from_proto(c).to_dict() for c in update.cryptos
                ]

                # Actualizar cache
                self.cached_top5 = cryptos[:5]

                # Actualizar cache de top50 (dict para búsqueda rápida)
                for crypto in cryptos:
                    self.cached_top50[crypto["id"]] = crypto

                log.info(f"Broadcasting {len(cryptos)} cryptos")

                # Top 5: Broadcast a TODOS
                await self.sio.emit("top5_update", {"cryptos": cryptos[:5]})

                # Top 50: Solo a suscritos
                await self.sio.emit(
                    "top50_update", {"cryptos": cryptos}, room="top50_subscribers"
                )

                log.info(f"Enviado top5 (broadcast) y top50 (sala)")

        except asyncio.CancelledError:
            log.info("Stream cancelado")
            raise
        except Exception as e:
            log.error(f"Error en stream_and_broadcast: {e}")
