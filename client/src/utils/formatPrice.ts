import { CryptoData, CryptoHistoryItem } from "@/types";

export function formatCryptoData(
  data: CryptoData[],
  rate: number
): CryptoData[] {
  return data.map((crypto) => ({
    ...crypto,
    current_price: crypto.current_price * rate,
    market_cap: crypto.market_cap * rate,
    fully_diluted_valuation: crypto.fully_diluted_valuation * rate,
    high_24h: crypto.high_24h * rate,
    low_24h: crypto.low_24h * rate,
    price_change_24h: crypto.price_change_24h * rate,
    price_change_percentage_24h: crypto.price_change_percentage_24h * rate,
  }));
}

export function formatCryptoHistoryData(
  data: CryptoHistoryItem[],
  rate: number
): CryptoHistoryItem[] {
  return data.map((item) => ({
    ...item,
    price: item.price * rate,
  }));
}
