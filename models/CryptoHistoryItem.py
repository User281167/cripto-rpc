from dataclasses import dataclass, field
import time


@dataclass
class CryptoHistoryItem:
    """Representa un snapshot de los precios de múltiples criptos en un momento dado."""

    id: str
    timestamp: int  # Momento del snapshot (Unix timestamp)
    price: float

    def factor_price(self, exchange: float = 1.0) -> "CryptoHistoryItem":
        """
        Devuelve el precio de una cripto específica en el formato de punto histórico.
        Retorna un dict que puede usarse para crear un mensaje Proto.
        """
        return CryptoHistoryItem(
            id=self.id, timestamp=self.timestamp, price=self.price * exchange
        )

    def to_dict(self) -> dict:
        return {"id": self.id, "timestamp": self.timestamp, "price": self.price}

    @classmethod
    def from_json(cls, data: dict) -> "CryptoHistoryItem":
        return cls(id=data["id"], timestamp=data["timestamp"], price=data["price"])

    @classmethod
    def from_proto(cls, id, proto_point):
        """
        Convierte un HistoricalPricePoint de protobuf a CryptoHistoryItem
        """
        return cls(id=id, timestamp=proto_point.timestamp, price=proto_point.price)
