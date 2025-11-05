import { tv } from "tailwind-variants";

export const title = tv({
  base: "tracking-tight inline font-semibold",
  variants: {
    color: {
      gold: "from-[#FEA000] to-[#cc8000]", // Dólar
      blue: "from-[#4F6BFF] to-[#3b53cc]", // Sistema principal
      silver: "from-[#A5BDEC] to-[#7f9ac2]", // Euro
      aqua: "from-[#01C89F] to-[#019a7a]", // Bitcoin
      coral: "from-[#FE4D68] to-[#cc3e54]",
      foreground: "dark:from-[#FFFFFF] dark:to-[#4B4B4B]", // Texto neutro
    },
    size: {
      sm: "text-3xl lg:text-4xl",
      md: "text-[2.3rem] lg:text-5xl",
      lg: "text-4xl lg:text-6xl",
    },
    fullWidth: {
      true: "w-full block",
    },
  },
  defaultVariants: {
    size: "md",
  },
  compoundVariants: [
    {
      color: ["gold", "blue", "silver", "aqua", "coral", "foreground"],
      class: "bg-clip-text text-transparent bg-gradient-to-b",
    },
  ],
});

export const subtitle = tv({
  base: "w-full md:w-1/2 my-2 text-lg lg:text-xl text-default-600 block max-w-full",
  variants: {
    fullWidth: {
      true: "!w-full",
    },
  },
  defaultVariants: {
    fullWidth: true,
  },
});
