"use client";

import { Loader2, ArrowRight } from "lucide-react";
import type { ButtonHTMLAttributes } from "react";

interface AuthButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  children: React.ReactNode;
}

export default function AuthButton({
  loading = false,
  children,
  className = "",
  disabled,
  ...props
}: AuthButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={`
        group
        flex
        w-full
        items-center
        justify-center
        gap-2
        rounded-lg
        bg-blue-600/45
        px-4
        py-3
        text-sm
        font-semibold
        text-white
        transition-all
        duration-200
        hover:bg-blue-500/60
        disabled:cursor-not-allowed
        disabled:opacity-60
        ${className}
      `}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <>
          {children}
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </>
      )}
    </button>
  );
}