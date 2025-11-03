from dataclasses import dataclass, field
import time


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
