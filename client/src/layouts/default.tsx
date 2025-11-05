import { Navbar } from "@/components/navbar";

export default function DefaultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex flex-col h-screen">
      <Navbar />
      <main className="container mx-auto max-w-7xl px-6 flex-grow pt-16">
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
