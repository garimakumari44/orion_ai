"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  FileText,
  Layers,
  ShieldCheck,
  Zap,
} from "lucide-react";

import Logo from "@/components/Logo";

interface AuthLayoutProps {
  children: ReactNode;
}

const capabilities = [
  {
    icon: FileText,
    title: "Reads the filings for you",
    description:
      "10-Ks, 10-Qs, transcripts, earnings calls and filings processed automatically.",
  },
  {
    icon: Layers,
    title: "Synthesizes across sources",
    description:
      "Connects financial reports, news, filings and research into one narrative.",
  },
  {
    icon: ShieldCheck,
    title: "Grounded answers",
    description:
      "Every statement links back to the original evidence with confidence scores.",
  },
  {
    icon: Zap,
    title: "Research in minutes",
    description:
      "From ticker or paper to a complete research report almost instantly.",
  },
];

export default function AuthLayout({
  children,
}: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen bg-black text-white">

      {/* LEFT PANEL */}

      <aside className="relative hidden flex-1 overflow-hidden border-r border-zinc-900 lg:flex">

        {/* background */}

        <div className="absolute inset-0 bg-gradient-to-br from-zinc-950 via-black to-black" />

        <div className="relative flex w-full flex-col justify-between px-24 py-16">

          {/* Header */}

          <header className="flex items-center justify-between">

            <Logo />

            <Link
              href="/docs"
              className="flex items-center gap-1 text-xs text-zinc-500 transition hover:text-white"
            >
              Documentation

              <ArrowUpRight className="h-4 w-4" />
            </Link>

          </header>

          {/* Hero */}

          <main className="max-w-2xl">

            <div className="mb-6 inline-flex items-center gap-2   mt-5 rounded-full border border-zinc-800 bg-zinc-950 px-3 py-1">

              <span className="h-2 w-2 rounded-full bg-green-500" />

              <span className="font-mono text-[11px] uppercase tracking-widest text-zinc-400">

                Enterprise AI Research Platform

              </span>

            </div>

            <h1 className="max-w-xl text-5xl font-semibold leading-tight">

              Research that thinks like an analyst.

            </h1>

            <p className="mt-6 max-w-lg text-zinc-400 leading-7">

              Orion AI combines retrieval, reasoning, and autonomous AI agents
              to produce research that is transparent, verifiable and
              institution-ready.

            </p>

            <div className="mt-12 grid grid-cols-2 gap-5">

              {capabilities.map((item) => (
                <div
                  key={item.title}
                  className="rounded-xl border border-zinc-900 bg-zinc-950/60 p-5 transition hover:border-blue-600/40"
                >
                  <item.icon
                    className="mb-4 h-5 w-5 text-blue-400/60"
                    strokeWidth={1.75}
                  />

                  <h3 className="text-sm font-semibold">
                    {item.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-zinc-400">
                    {item.description}
                  </p>

                </div>
              ))}

            </div>

          </main>

          {/* Footer */}

          <footer className="flex items-center justify-between text-xs p-5 text-zinc-500">

            <span>
              Built for AI Researchers • ML Engineers • Analysts
            </span>

            <span>© 2026 Orion AI</span>

          </footer>

        </div>

      </aside>

      
{/* RIGHT PANEL */}

{/* RIGHT PANEL */}

<main className="flex flex-1 items-center ml-3 justify-center  py-4">

  <div className="w-full max-w-sm">

    <div className="mb-4 flex justify-center lg:hidden">
      <Logo />
    </div>

    <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-6 shadow-xl">

      {children}

    </div>

    <p className="mt-4 text-center text-xs leading-5 text-zinc-500">
      By continuing you agree to the Terms of Service and Privacy Policy.
    </p>

  </div>

</main>

    </div>
  );
}