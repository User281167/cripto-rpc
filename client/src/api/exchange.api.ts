import { ExchangeRate } from "@/types";
import { PROJECT_ENV } from "@/utils/env";

export const getExchangeRates = async (): Promise<ExchangeRate[]> => {
  const response = await fetch(`${PROJECT_ENV.API_URL}/exchanges`);

  const format: ExchangeRate[] = await response.json();

  return format;
};
