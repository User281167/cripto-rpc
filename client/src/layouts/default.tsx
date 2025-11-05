import { Navbar } from "@/components/navbar";
import { CryptoLine } from "@/components/crypto-line";
import { useSocket } from "@/context/SocketContext";

export default function DefaultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { top5 } = useSocket();

  return (
    <div className="relative flex flex-col h-screen">
      <Navbar />
      <CryptoLine data={top5} />

      <main className="container mx-auto max-w-7xl px-6 flex-grow">
        {children}
      </main>

      <footer className="w-full flex flex-col items-center justify-center py-6 border-t border-default-200 text-sm bg-default-50">
        <p className="text-default-500 mb-1">
          Sistema Distribuido de Reportes Financieros Automatizados
        </p>
      </footer>
    </div>
  );
}
