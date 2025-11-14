import { Kbd } from "@heroui/react";
import { Autocomplete, AutocompleteItem } from "@heroui/autocomplete";
import { useNavigate } from "react-router-dom";

import { SearchIcon } from "@/components/icons";
import { useSocket } from "@/context/SocketContext";

export const CryptoSearch = () => {
  const { top50 } = useSocket();
  const navigate = useNavigate();

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
      onSelectionChange={(key) => {
        const selected = top50.find((c) => c.id === key);

        if (selected) navigate(`/${selected.id}`);
      }}
    >
      {top50.map((crypto) => (
        <AutocompleteItem key={crypto.id}>{crypto.name}</AutocompleteItem>
      ))}
    </Autocomplete>
  );
};
