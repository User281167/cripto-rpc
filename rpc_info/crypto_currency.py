from dataclasses import dataclass, field
import time

from generated import crypto_pb2


@dataclass
class CryptoCurrency:
    id: str
    symbol: str
    name: str
    image: str
    current_price: float
    market_cap: int
    market_cap_rank: int
    fully_diluted_valuation: int
    total_volume: int
    high_24h: float
    low_24h: float
    price_change_24h: float
    price_change_percentage_24h: float
    last_updated: str

    @classmethod
    def from_json(cls, data):
        keys = cls.__annotations__.keys()
        filtered = {k: data[k] for k in keys if k in data}
        return cls(**filtered)

    def to_dict(self):
        return self.__dict__

    def to_proto(self):
        return crypto_pb2.Crypto(
            id=self.id,
            symbol=self.symbol,
            name=self.name,
            image=self.image,
            current_price=self.current_price,
            market_cap=self.market_cap,
            market_cap_rank=self.market_cap_rank,
            fully_diluted_valuation=self.fully_diluted_valuation,
            total_volume=self.total_volume,
            high_24h=self.high_24h,
            low_24h=self.low_24h,
            price_change_24h=self.price_change_24h,
            price_change_percentage_24h=self.price_change_percentage_24h,
            last_updated=self.last_updated,
        )

    def update_price_factor(self, exchange: float) -> "CryptoCurrency":
        self.current_price *= exchange
        self.high_24h *= exchange
        self.low_24h *= exchange
        self.price_change_24h *= exchange
        return self


@dataclass
class CryptoHistoryItem:
    """Representa un snapshot de los precios de múltiples criptos en un momento dado."""

    timestamp: int  # Momento del snapshot (Unix timestamp)
    prices: dict[str, float] = field(default_factory=dict)  # {ID_cripto: precio, ...}

    @classmethod
    def from_raw_data(cls, raw_data: list[dict]) -> "CryptoHistoryItem":
        """Crea una instancia a partir de la lista de diccionarios de la API."""
        current_time = int(time.time())

        # Mapea solo el ID y el precio actual de todos los elementos en los datos crudos
        price_snapshot = {
            d["id"]: d["current_price"]
            for d in raw_data
            if "id" in d and "current_price" in d
        }

        return cls(timestamp=current_time, prices=price_snapshot)

    def to_historical_point(self, crypto_id: str, exchange: float = 1.0) -> dict | None:
        """
        Devuelve el precio de una cripto específica en el formato de punto histórico.
        Retorna un dict que puede usarse para crear un mensaje Proto.
        """
        price = self.prices.get(crypto_id)

        if price is None:
            return None

        return {"timestamp": self.timestamp, "price": price * exchange}
