import { Link } from "@heroui/link";

import { CryptoData } from "@/types";

interface CryptoTableProps {
  data: CryptoData[];
}

export const CryptoLine = ({ data }: CryptoTableProps) => {
  return (
    <div className="md:w-9/12 mx-auto border-b border-gray-300">
      <div className="flex items-center justify-center space-x-4 overflow-x-auto py-4 w-full">
        {data.map((crypto) => (
          <Link
            key={crypto.id}
            className="flex flex-col items-center justify-center"
            href={`/${crypto.id}`}
          >
            <img alt={crypto.name} className="w-10 h-10" src={crypto.image} />
            <span>{crypto.name}</span>
            <span
              className={
                crypto.price_change_percentage_24h >= 0
                  ? "text-green-500"
                  : "text-red-500"
              }
            >
              {crypto.price_change_percentage_24h.toFixed(2)}%
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
};
