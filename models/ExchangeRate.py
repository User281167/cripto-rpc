from dataclasses import dataclass
from generated import crypto_pb2


@dataclass
class ExchangeRate:
    currency: str
    rate: float

    def to_dict(self):
        return {"currency": self.currency, "rate": self.rate}

    @classmethod
    def from_dict(cls, data):
        """
        {
        "currency": rate,
        }
        """
        name, rate = data
        return cls(currency=name, rate=rate)

    @classmethod
    def from_proto(cls, proto):
        return cls(currency=proto.currency, rate=proto.rate)

    def to_proto(self):
        return crypto_pb2.ExchangeRate(currency=self.currency, rate=self.rate)
