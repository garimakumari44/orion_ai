import type { Metadata } from "next";
import "./globals.css";

import { AuthProvider } from "@/providers/auth-provider";

export const metadata: Metadata = {
  title: "Orion AI — Multi-Agent Analyst",
  description: "Autonomous AI system for developers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className="h-full"
    >
      <body className="h-screen w-screen overflow-hidden bg-[#04091A] text-white antialiased">
        <AuthProvider>
          <div className="h-full w-full">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}