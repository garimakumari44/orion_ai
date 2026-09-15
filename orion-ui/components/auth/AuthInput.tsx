"use client";

import { forwardRef } from "react";

interface AuthInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

const AuthInput = forwardRef<HTMLInputElement, AuthInputProps>(
  ({ label, error, className = "", ...props }, ref) => {
    return (
      <div className="space-y-2">
        <label
          htmlFor={props.id}
          className="block text-xs font-medium text-zinc-400"
        >
          {label}
        </label>

        <input
          ref={ref}
          {...props}
          className={`
            w-full rounded-lg
            border border-zinc-800
            bg-zinc-950
            px-4 py-3
            text-sm text-white
            placeholder:text-zinc-500
            outline-none
            transition-all
            duration-200
            focus:border-blue-300
            focus:ring-2
            focus:ring-blue-500/20
            disabled:cursor-not-allowed
            disabled:opacity-60
            ${className}
          `}
        />

        {error && (
          <p className="text-xs text-red-400">
            {error}
          </p>
        )}
      </div>
    );
  }
);

AuthInput.displayName = "AuthInput";

export default AuthInput;