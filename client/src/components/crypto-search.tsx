import { Kbd } from "@heroui/react";
import { Autocomplete, AutocompleteItem } from "@heroui/autocomplete";
import { Link } from "@heroui/react";

import { SearchIcon } from "@/components/icons";
import { useSocket } from "@/context/SocketContext";

export const CryptoSearch = () => {
  const { top50 } = useSocket();

  return (
    <Autocomplete
      aria-label="Search"
      endContent={
        <Kbd className="hidden lg:inline-block" keys={["command"]}>
          K
        </Kbd>
      }
      placeholder="Search..."
      startContent={
        <SearchIcon className="text-base text-default-400 pointer-events-none flex-shrink-0" />
      }
      type="search"
    >
      {top50.map((crypto) => (
        <AutocompleteItem key={crypto.name}>
          <Link className="w-full text-normal" href={`/${crypto.id}`}>
            {crypto.name}
          </Link>
        </AutocompleteItem>
      ))}
    </Autocomplete>
  );
};
