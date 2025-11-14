import { Link } from "@heroui/link";
import { button as buttonStyles } from "@heroui/theme";

import { siteConfig } from "@/config/site";
import { title, subtitle } from "@/components/primitives";
import { GithubIcon } from "@/components/icons";
import DefaultLayout from "@/layouts/default";
import { useSocket } from "@/context/SocketContext";
import { CryptoTable } from "@/components/crypto-table";
import { CryptoReports } from "@/components/crypto-reports";

export default function IndexPage() {
  const { top50 } = useSocket();

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center justify-center">
          <span className={title({ color: "aqua" })}>
            Precios en tiempo real&nbsp;
          </span>

          <br />
          <span className={title()}>de criptomonedas</span>
          <br />

          <span className={subtitle()}>
            Visualiza los precios de las criptos más relevantes y su variación
            diaria. Ideal para traders, analistas y curiosos del mundo
            financiero.
          </span>
        </div>

        <div className="flex gap-3">
          <Link
            isExternal
            className={buttonStyles({
              color: "primary",
              radius: "full",
              variant: "shadow",
            })}
            href={siteConfig.links.docs}
          >
            Documentación
          </Link>
          <Link
            isExternal
            className={buttonStyles({ variant: "bordered", radius: "full" })}
            href={siteConfig.links.github}
          >
            <GithubIcon size={20} />
            GitHub
          </Link>
        </div>
      </section>

      <CryptoReports />

      <section className="pb-10 md:pb-16">
        <CryptoTable data={top50} isLoading={!top50.length} />
      </section>
    </DefaultLayout>
  );
}
