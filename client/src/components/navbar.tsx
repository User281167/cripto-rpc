import { Autocomplete, AutocompleteItem, Link } from "@heroui/react";
import {
  Navbar as HeroUINavbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  NavbarMenuToggle,
  NavbarMenu,
  NavbarMenuItem,
} from "@heroui/react";
import { link as linkStyles } from "@heroui/react";
import clsx from "clsx";
import { IconCurrencyDollar } from "@tabler/icons-react";

import { CryptoSearch } from "./crypto-search";
import { EmailSuscribe } from "./email-suscribe";
import { EmailUnsuscribe } from "./email-unsuscribe";

import { siteConfig } from "@/config/site";
import { ThemeSwitch } from "@/components/theme-switch";
import { GithubIcon } from "@/components/icons";
import { useExchange } from "@/context/ExchangeContext";

export const Navbar = () => {
  const { currentExchange, exchanges, setCurrentExchange } = useExchange();

  const selectExchangeItems = exchanges.map((exchange) => ({
    key: exchange.currency.toLowerCase(),
    label: exchange.currency,
  }));

  const selectExchangeValue = currentExchange?.currency.toLowerCase();

  const currencySearch = (
    <Autocomplete
      aria-label="currency"
      className="w-full md:max-w-36"
      defaultInputValue={selectExchangeValue}
      endContent={<IconCurrencyDollar />}
      placeholder="USD"
      type="search"
      onSelectionChange={(key) => {
        setCurrentExchange(key);
      }}
    >
      {selectExchangeItems.map((item) => (
        <AutocompleteItem key={item.key}>{item.label}</AutocompleteItem>
      ))}
    </Autocomplete>
  );

  return (
    <HeroUINavbar maxWidth="xl" position="sticky">
      <NavbarContent className="basis-1/5 sm:basis-full" justify="start">
        <NavbarBrand className="gap-3 max-w-fit">
          <Link
            className="flex justify-start items-center gap-1"
            color="foreground"
            href="/"
          >
            <img alt="Cryto-RPC" className="w-10 h-10" src="/favicon.ico" />
            <p className="font-bold text-inherit">Cryto-RPC</p>
          </Link>
        </NavbarBrand>

        <div className="hidden lg:flex gap-4 justify-start ml-2">
          {siteConfig.navItems.map((item) => (
            <NavbarItem key={item.href}>
              <Link
                className={clsx(
                  linkStyles({ color: "foreground" }),
                  "data-[active=true]:text-primary data-[active=true]:font-medium"
                )}
                color="foreground"
                href={item.href}
              >
                {item.label}
              </Link>
            </NavbarItem>
          ))}
        </div>
      </NavbarContent>

      <NavbarContent
        className="hidden sm:flex basis-1/5 sm:basis-full"
        justify="end"
      >
        <NavbarItem className="hidden sm:flex gap-2">
          <Link isExternal href={siteConfig.links.github} title="GitHub">
            <GithubIcon className="text-default-500" />
          </Link>
          <ThemeSwitch />
        </NavbarItem>

        <NavbarItem className="hidden sm:flex">
          <EmailSuscribe />
        </NavbarItem>

        <NavbarItem className="hidden sm:flex">
          <EmailUnsuscribe />
        </NavbarItem>

        <NavbarItem className="hidden lg:flex">
          <CryptoSearch />
        </NavbarItem>

        <NavbarItem className="hidden sm:flex">{currencySearch}</NavbarItem>
      </NavbarContent>

      <NavbarContent className="sm:hidden basis-1 pl-4" justify="end">
        <Link isExternal href={siteConfig.links.github}>
          <GithubIcon className="text-default-500" />
        </Link>
        <ThemeSwitch />
        <NavbarMenuToggle />
      </NavbarContent>

      <NavbarMenu>
        <CryptoSearch />
        {currencySearch}

        <div className="mx-4 mt-2 flex flex-col gap-2">
          {siteConfig.navMenuItems.map((item, index) => (
            <NavbarMenuItem key={`${item}-${index}`}>
              <Link
                color={
                  index === 2
                    ? "primary"
                    : index === siteConfig.navMenuItems.length - 1
                      ? "danger"
                      : "foreground"
                }
                href="#"
                size="lg"
              >
                {item.label}
              </Link>
            </NavbarMenuItem>
          ))}
        </div>
      </NavbarMenu>
    </HeroUINavbar>
  );
};
