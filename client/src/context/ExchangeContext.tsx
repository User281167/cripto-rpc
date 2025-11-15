import React, { createContext, useContext, useEffect, useState } from "react";

import { ExchangeRate } from "@/types";
import { getExchangeRates } from "@/api/exchange.api";

interface ExchangeContextType {
  exchanges: ExchangeRate[];
  currentExchange: ExchangeRate | null;
  setCurrentExchange: (id: string | null) => void;
}

const ExchangeContext = createContext<ExchangeContextType>({
  exchanges: [],
  currentExchange: null,
  setCurrentExchange: (id: string | null) => {},
});

export const ExchangeProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [exchanges, setExchanges] = useState<ExchangeRate[]>([]);
  const [currentExchange, setCurrentExchange] = useState<ExchangeRate | null>(
    null
  );

  useEffect(() => {
    getExchangeRates().then((exchanges) => {
      setExchanges(exchanges);

      // por defecto USD
      setCurrentExchange(
        exchanges.find((e) => e.currency.toLowerCase() === "usd") || null
      );
    });
  }, []);

  const _setCurrentExchange = (id: string | null) =>
    id &&
    setCurrentExchange(
      exchanges.find((e) => e.currency.toLowerCase() === id) || null
    );

  return (
    <ExchangeContext.Provider
      value={{
        exchanges,
        currentExchange,
        setCurrentExchange: _setCurrentExchange,
      }}
    >
      {children}
    </ExchangeContext.Provider>
  );
};

export const useExchange = () => useContext(ExchangeContext);
