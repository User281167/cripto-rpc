import {
  Table,
  TableHeader,
  TableBody,
  TableColumn,
  TableRow,
  TableCell,
} from "@heroui/react";
import { Link } from "@heroui/react";
import { Spinner } from "@heroui/react";
import { useState, useMemo } from "react";

import { CryptoData } from "@/types";

interface CryptoTableProps {
  data: CryptoData[];
  isLoading?: boolean;
}

export const CryptoTable = ({ data, isLoading = false }: CryptoTableProps) => {
  const isEmpty = !data || data.length === 0;

  const [sort, setSort] = useState({
    column: "market_cap_rank",
    direction: "ascending",
  });

  const sortedData = useMemo(() => {
    if (!data.length) return [];

    const sorted = [...data].sort((a, b) => {
      const col = sort.column as keyof CryptoData;
      const valA = a[col];
      const valB = b[col];

      // Comparación numérica o alfabética
      const isNumeric = typeof valA === "number" && typeof valB === "number";
      const cmp = isNumeric
        ? valA - valB
        : String(valA).localeCompare(String(valB));

      return sort.direction === "ascending" ? cmp : -cmp;
    });

    return sorted;
  }, [data, sort]);

  return (
    <div className="w-full overflow-x-auto min-h-[400px]">
      {isLoading || isEmpty ? (
        <div className="flex justify-center items-center h-full py-10">
          <Spinner label="Cargando criptomonedas..." />
        </div>
      ) : (
        <Table
          isHeaderSticky
          aria-label="Tabla de las 50 principales criptomonedas"
          sortDescriptor={sort}
          onSortChange={setSort}
          classNames={{
            base: "max-h-[90vh] overflow-y-auto overflow-x-hidden",
            table: "min-h-[400px]",
          }}
        >
          <TableHeader>
            <TableColumn key="market_cap_rank" allowsSorting>
              #
            </TableColumn>
            <TableColumn key="name" allowsSorting>
              Nombre
            </TableColumn>
            <TableColumn key="symbol" allowsSorting>
              Símbolo
            </TableColumn>
            <TableColumn key="current_price" allowsSorting>
              Precio
            </TableColumn>
            <TableColumn key="high_24h" allowsSorting>
              Máximo 24h
            </TableColumn>
            <TableColumn key="low_24h" allowsSorting>
              Mínimo 24h
            </TableColumn>
            <TableColumn key="price_change_24h" allowsSorting>
              Variación 24h
            </TableColumn>
            <TableColumn key="price_change_percentage_24h" allowsSorting>
              % Variación
            </TableColumn>
            <TableColumn key="market_cap" allowsSorting>
              Market Cap
            </TableColumn>
            <TableColumn key="total_volume" allowsSorting>
              Volumen
            </TableColumn>
            <TableColumn key="last_updated">Última Actualización</TableColumn>
          </TableHeader>

          <TableBody items={sortedData}>
            {(crypto) => (
              <TableRow key={crypto.id}>
                <TableCell>{crypto.market_cap_rank}</TableCell>
                <TableCell>
                  <Link
                    className="flex items-center gap-2"
                    href={`/${crypto.id}`}
                  >
                    <img
                      alt={crypto.name}
                      className="w-5 h-5"
                      src={crypto.image}
                    />
                    {crypto.name}
                  </Link>
                </TableCell>
                <TableCell>{crypto.symbol.toUpperCase()}</TableCell>
                <TableCell>${crypto.current_price.toLocaleString()}</TableCell>
                <TableCell>${crypto.high_24h.toLocaleString()}</TableCell>
                <TableCell>${crypto.low_24h.toLocaleString()}</TableCell>
                <TableCell
                  className={
                    crypto.price_change_24h >= 0
                      ? "text-green-500"
                      : "text-red-500"
                  }
                >
                  {crypto.price_change_24h.toFixed(2)}
                </TableCell>
                <TableCell
                  className={
                    crypto.price_change_percentage_24h >= 0
                      ? "text-green-500"
                      : "text-red-500"
                  }
                >
                  {crypto.price_change_percentage_24h.toFixed(2)}%
                </TableCell>
                <TableCell>${crypto.market_cap.toLocaleString()}</TableCell>
                <TableCell>${crypto.total_volume.toLocaleString()}</TableCell>
                <TableCell>
                  {new Date(crypto.last_updated).toLocaleString()}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </div>
  );
};
