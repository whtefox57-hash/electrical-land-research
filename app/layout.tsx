import PWA from './pwa';
import type { Metadata, Viewport } from "next";
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
  applicationName: "Syncranicity Deal Desk",
  manifest: "/home-screen-v2.webmanifest",
  appleWebApp: {capable:true,title:"Deal Desk",statusBarStyle:"black-translucent"},
  icons: {
    apple: "/apple-touch-icon-v2.png",
    icon: "/favicon-v2-32.png",
    shortcut: "/favicon-v2-32.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased"><PWA/>{children}</body>
    </html>
  );
}

export const viewport: Viewport={themeColor:"#111827",width:"device-width",initialScale:1};
