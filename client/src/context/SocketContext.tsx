// SocketContext.tsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";
import { useLocation } from "react-router-dom";

import { CryptoData } from "@/types";

interface SocketContextType {
  socket: Socket | null;
  top5: any[];
  top50: any[];
}

const SocketContext = createContext<SocketContextType>({
  socket: null,
  top5: [],
  top50: [],
});

export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [top5, setTop5] = useState<CryptoData[]>([]);
  const [top50, setTop50] = useState<CryptoData[]>([]);

  const location = useLocation();

  useEffect(() => {
    const newSocket = io(import.meta.env.VITE_SOCKET_URL, {
      transports: ["websocket", "polling"],
    });

    newSocket.on("connect", () => {
      console.log("Conectado:", newSocket.id);
    });

    // Siempre a la escucha de actualizaciones
    newSocket.on("top5_update", (data) => {
      const processedData: CryptoData[] = Array.isArray(data)
        ? data
        : data.cryptos || [];

      setTop5(processedData);
    });

    // Solo recibe cuando está en la página principal
    newSocket.on("top50_update", (data) => {
      const processedData: CryptoData[] = Array.isArray(data)
        ? data
        : data.cryptos || [];

      setTop50(processedData);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  // Suscribirse/desuscribirse según la ruta
  useEffect(() => {
    if (!socket) return;

    if (location.pathname === "/") {
      socket.emit("subscribe_top50");
    } else {
      socket.emit("unsubscribe_top50");
    }
  }, [location.pathname, socket]);

  return (
    <SocketContext.Provider value={{ socket, top5, top50 }}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = () => useContext(SocketContext);
