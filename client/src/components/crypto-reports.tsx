import { Button } from "@heroui/react";
import { addToast } from "@heroui/react";
import {
  IconFileTypeXls,
  IconFileTypePdf,
  IconFileTypeDocx,
  IconFileTypePng,
} from "@tabler/icons-react";

import {
  getCryptoReport,
  getExecutiveReport,
  getGraphReport,
  getTrendReport,
} from "@/api/doc.api";
import { ReportApi } from "@/types/models";

export const CryptoReports = () => {
  const generateUrl = (url: string, filename: string) => {
    const a = document.createElement("a");

    a.href = url;
    a.download = filename;

    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
  };

  const downloadCryptoFile = (callback: () => Promise<ReportApi>) => {
    addToast({
      title: "Generando reporte",
      description: "El reporte de criptomonedas se esta generando.",
      color: "primary",
      promise: callback()
        .then((res: ReportApi) => {
          addToast({
            title: "Reporte generado",
            description:
              "El reporte de criptomonedas se ha generado exitosamente.",
            color: "success",
          });

          generateUrl(res.url, res.filename);
        })
        .catch(() => {
          addToast({
            title: "Error al generar el reporte",
            description:
              "El reporte de criptomonedas no pudo ser generado. Inténtalo de nuevo o más tarde.",
            color: "danger",
          });
        }),
    });
  };

  return (
    <section className="pb-10 md:pb-16 w-full flex flex-col gap-4 md:flex-row align-center justify-center">
      <Button
        className="bg-green-500 text-white"
        endContent={<IconFileTypeXls />}
        onClick={() => downloadCryptoFile(getCryptoReport)}
      >
        Reporte de criptomonedas
      </Button>

      <Button
        className="bg-blue-500 text-white"
        endContent={<IconFileTypeDocx />}
        onClick={() => downloadCryptoFile(getTrendReport)}
      >
        Reporte de tendencias
      </Button>

      <Button
        className="bg-red-500 text-white"
        endContent={<IconFileTypePdf />}
        onClick={() => downloadCryptoFile(getExecutiveReport)}
      >
        Reporte de tendencias
      </Button>

      <Button
        className="bg-gray-200 dark:bg-gray-800 dark:text-gray-200"
        endContent={<IconFileTypePng />}
        onClick={() => downloadCryptoFile(getGraphReport)}
      >
        Reporte de variación
      </Button>
    </section>
  );
};
