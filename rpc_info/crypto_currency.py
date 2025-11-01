from dataclasses import dataclass
import crypto_pb2 as crypto_pb2


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
    def from_dict(cls, data):
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
