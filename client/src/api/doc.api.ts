import { ReportApi } from "@/types/models";
import { PROJECT_ENV } from "@/utils/env";

export const getCryptoReport = async (currency = "usd"): Promise<ReportApi> => {
  // api retorna una seria de bytes del archivo
  // Crear enlace de descarga de archivo

  const response = await fetch(
    `${PROJECT_ENV.API_URL}/reports/crypto?currency=${currency}`
  );
  const blob = await response.blob();

  // Recuperar nombre de archivo desde el header
  const disposition = response.headers.get("content-disposition");
  const match = disposition?.match(/filename=([^;]+)/);
  const filename = match ? match[1] : "reporte.xlsx";

  return { url: URL.createObjectURL(blob), filename } as ReportApi;
};

export const getTrendReport = async (currency = "usd"): Promise<ReportApi> => {
  const response = await fetch(
    `${PROJECT_ENV.API_URL}/reports/trend?currency=${currency}`
  );
  const blob = await response.blob();

  const disposition = response.headers.get("content-disposition");
  const match = disposition?.match(/filename=([^;]+)/);
  const filename = match ? match[1] : "reporte.docx";

  return { url: URL.createObjectURL(blob), filename } as ReportApi;
};

export const getExecutiveReport = async (
  currency = "usd"
): Promise<ReportApi> => {
  const response = await fetch(
    `${PROJECT_ENV.API_URL}/reports/executive?currency=${currency}`
  );
  const blob = await response.blob();

  const disposition = response.headers.get("content-disposition");
  const match = disposition?.match(/filename=([^;]+)/);
  const filename = match ? match[1] : "reporte.pdf";

  return { url: URL.createObjectURL(blob), filename } as ReportApi;
};

export const getGraphReport = async (currency = "usd"): Promise<ReportApi> => {
  const response = await fetch(
    `${PROJECT_ENV.API_URL}/reports/graph?currency=${currency}`
  );
  const blob = await response.blob();

  const disposition = response.headers.get("content-disposition");
  const match = disposition?.match(/filename=([^;]+)/);
  const filename = match ? match[1] : "grafico_barras.png";

  return { url: URL.createObjectURL(blob), filename } as ReportApi;
};
