import redis
import json
import time
import uuid
import logging
from enum import Enum

from utils import ProjectEnv
from models import CryptoCurrency, CryptoHistoryItem

log = logging.getLogger(__name__)

MAX_HISTORY_SIZE = (
    24 * 60 * 60 // 30
)  # 24 horas de datos, actualizados cada 30 segundos


class CacheItem(Enum):
    CRYPTO_DATA = "crypto:data"
    CRYPTO_LAST_UPDATED = "crypto:last_updated"
    CRYPTO_HISTORY = "crypto:history"
    CURRENCY_EXCHANGE = "currency:exchange"


class DataCache:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataCache, cls).__new__(cls)

        return cls._instance

    def __init__(
        self,
        host=ProjectEnv.RPC_INFO_REDIS_HOST,
        port=ProjectEnv.RPC_INFO_REDIS_PORT,
        db=0,
    ):
        if self._initialized and self.alive():
            return

        print("Conectando a Redis...")
        print(f"   - Host: {host}")
        print(f"   - Puerto: {port}")
        print(f"   - Base de datos: {db}")
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self._initialized = True

    def acquire_lock(self, lock_name: str, expire: int = 30) -> str | None:
        """
        Intenta adquirir un lock. Retorna un token si lo logra, o None si ya está tomado.
        Esto para que varias instancias no se puedan ejecutar al mismo tiempo.
        Evitar duplicados.

        args:
            lock_name (str): Nombre del lock.
            expire (int): Tiempo de expiración en segundos.
        """
        token = str(uuid.uuid4())
        success = self.redis.set(lock_name, token, nx=True, ex=expire)
        return token if success else None

    def release_lock(self, lock_name: str, token: str) -> bool:
        """
        Libera el lock solo si el token coincide (previene que otro proceso lo libere).
        """
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        released = self.redis.eval(script, 1, lock_name, token) == 1

        if not released:
            log.warning(f"Lock {lock_name} no released by {token}")

        return released

    def with_lock(lock_name, expire=30):
        lock_name += ":lock"

        def decorator(func):
            def wrapper(self, *args, **kwargs):
                token = self.acquire_lock(lock_name, expire)
                if not token:
                    return
                try:
                    return func(self, *args, **kwargs)
                finally:
                    self.release_lock(lock_name, token)

            return wrapper

        return decorator

    @with_lock(CacheItem.CRYPTO_DATA.value)
    def save_crypto_data(self, cryptos: list[CryptoCurrency]):
        self.redis.set(
            CacheItem.CRYPTO_DATA.value, json.dumps([c.to_dict() for c in cryptos])
        )
        self.redis.set(CacheItem.CRYPTO_LAST_UPDATED.value, int(time.time()))

    @with_lock(CacheItem.CRYPTO_HISTORY.value)
    def save_crypto_history(self, snapshot: list[CryptoHistoryItem]):
        # Usar to_dict() en lugar de __dict__ para asegurar formato correcto
        serialized = json.dumps([item.to_dict() for item in snapshot])

        self.redis.lpush(CacheItem.CRYPTO_HISTORY.value, serialized)
        self.redis.ltrim(CacheItem.CRYPTO_HISTORY.value, 0, MAX_HISTORY_SIZE - 1)

    @with_lock(CacheItem.CURRENCY_EXCHANGE.value)
    def save_exchange(self, exchange_data: dict):
        self.redis.set(CacheItem.CURRENCY_EXCHANGE.value, json.dumps(exchange_data))

    def get_crypto_data(self) -> list[CryptoCurrency]:
        raw = self.redis.get(CacheItem.CRYPTO_DATA.value)
        return [CryptoCurrency.from_json(d) for d in json.loads(raw)] if raw else []

    def get_crypto_history(self) -> list[CryptoHistoryItem]:
        raw = self.redis.lrange(CacheItem.CRYPTO_HISTORY.value, 0, -1)

        history: list[CryptoHistoryItem] = []
        for snapshot_json in raw:
            try:
                snapshot_list = json.loads(snapshot_json)  # esto es una lista de dicts
                # Asegurarse de que cada item es un diccionario antes de desempaquetar
                for item in snapshot_list:
                    if isinstance(item, dict):
                        try:
                            history.append(CryptoHistoryItem(**item))
                        except TypeError as e:
                            log.error(f"Error creando CryptoHistoryItem desde dict: {e}, item: {item}")
                    elif isinstance(item, str):
                        # Si es un string, intentar parsearlo como JSON
                        try:
                            item_dict = json.loads(item)
                            if isinstance(item_dict, dict):
                                history.append(CryptoHistoryItem(**item_dict))
                            else:
                                log.warning(f"Item parseado no es un dict: {type(item_dict)}")
                        except Exception as e:
                            log.warning(f"Error parseando item del historial: {e}, item: {item}")
                    else:
                        log.warning(f"Item del historial tiene tipo inesperado: {type(item)}, valor: {item}")
            except json.JSONDecodeError as e:
                log.error(f"Error parseando JSON del historial: {e}, raw: {snapshot_json[:100]}")
            except Exception as e:
                log.error(f"Error procesando snapshot del historial: {e}")

        return history

    def get_exchange(self) -> dict:
        raw = self.redis.get(CacheItem.CURRENCY_EXCHANGE.value)
        return json.loads(raw)

    def close(self):
        self.redis.close()

    def alive(self) -> bool:
        try:
            return self.redis.ping()
        except:
            return False
