from dataclasses import dataclass


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
