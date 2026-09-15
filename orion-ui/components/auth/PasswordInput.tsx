"use client";

import { forwardRef, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

interface PasswordInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  (
    {
      label = "Password",
      error,
      className = "",
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);

    return (
      <div className="space-y-2">
        <label
          htmlFor={props.id}
          className="block text-xs font-medium text-zinc-400"
        >
          {label}
        </label>

        <div className="relative">
          <input
            ref={ref}
            {...props}
            type={showPassword ? "text" : "password"}
            className={`
              w-full rounded-lg
              border border-zinc-800
              bg-zinc-950
              px-4 py-3 pr-12
              text-sm text-white
              placeholder:text-zinc-500
              outline-none
              transition-all
              duration-200
              focus:border-blue-200
              focus:ring-2
              focus:ring-blue-500/20
              ${className}
            `}
          />

          <button
            type="button"
            onClick={() => setShowPassword((prev) => !prev)}
            className="
              absolute right-3 top-1/2
              -translate-y-1/2
              text-zinc-500
              transition
              hover:text-white
            "
          >
            {showPassword ? (
              <EyeOff size={18} />
            ) : (
              <Eye size={18} />
            )}
          </button>
        </div>

        {error && (
          <p className="text-xs text-red-400">
            {error}
          </p>
        )}
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";

export default PasswordInput;