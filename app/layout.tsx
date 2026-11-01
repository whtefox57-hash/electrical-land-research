import type { Metadata } from "next";
import "./globals.css";
import "./research-hub.css";
import "./atlas.css";
import "./oct13-research.css";
import "./oct19-research.css";
import "./oct22-research.css";
import "./buyer-research.css";
import "./origination.css";
import "./data-centers.css";

export const metadata: Metadata = {
  title: "Syncranicity Deal Desk",
  description: "Private land research and decision workspace for Syncranicity LLC.",
  icons: {
    icon: "https://syncranicity-land.whtefox57.chatgpt.site/home-icons/syncranicity-deal-desk/favicon-v2-32.png?v=art2",
    shortcut: "https://syncranicity-land.whtefox57.chatgpt.site/home-icons/syncranicity-deal-desk/favicon-v2-32.png?v=art2",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en"><head><link rel="apple-touch-icon" sizes="180x180" href="https://syncranicity-land.whtefox57.chatgpt.site/home-icons/syncranicity-deal-desk/apple-touch-icon-v2.png?v=art2" /><link rel="icon" type="image/png" sizes="32x32" href="https://syncranicity-land.whtefox57.chatgpt.site/home-icons/syncranicity-deal-desk/favicon-v2-32.png?v=art2" /><link rel="manifest" href="/home-screen-v2.webmanifest" /></head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
