import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

import DefaultLayout from "@/layouts/default";
import { useSocket } from "@/context/SocketContext";
import { CryptoHistoryItem } from "@/types";
import { subtitle } from "@/components/primitives";

export default function CryptoPage() {
  const { socket, joinCryptoRoom, leaveCryptoRoom } = useSocket();
  const { id } = useParams();
  const [cryptoData, setCryptoData] = useState<CryptoHistoryItem[] | null>(
    null
  );
  const [chartData, setChartData] = useState<any[]>([]);

  // Unirse a la sala de esta crypto específica
  useEffect(() => {
    if (!socket || !id) return;

    // Unirse a la sala
    joinCryptoRoom(id);

    // Escuchar actualizaciones de esta moneda
    const handleCoinUpdate = (data: any) => {
      const processedData: CryptoHistoryItem[] = Array.isArray(data)
        ? data
        : data.data || [];

      setCryptoData(processedData);
    };

    socket.on("crypto_update", handleCoinUpdate);

    // Cleanup: salir de la sala y remover listener
    return () => {
      leaveCryptoRoom(id);
      socket.off("crypto_update", handleCoinUpdate);
    };
  }, [socket, id, joinCryptoRoom, leaveCryptoRoom]);

  useEffect(() => {
    if (!cryptoData) return;

    const cleanedData = cryptoData.map((item) => ({
      timestamp: new Date(item.timestamp * 1000).toLocaleTimeString(),
      price: item.price,
    }));

    setChartData(cleanedData);
  }, [cryptoData]);

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="w-full">
          <h2 className={subtitle()}>Historial de precios: {id}</h2>

          <ResponsiveContainer height={400} width="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Line dataKey="price" stroke="#8884d8" type="monotone" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </DefaultLayout>
  );
}
