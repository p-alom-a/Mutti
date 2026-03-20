import { Pirata_One } from "next/font/google";
import "./globals.css";

const pirataOne = Pirata_One({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-pirata",
});

export const metadata = {
  title: "Mutti",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="https://use.typekit.net/pve2awf.css" />
      </head>
      <body className={pirataOne.variable}>{children}</body>
    </html>
  );
}
