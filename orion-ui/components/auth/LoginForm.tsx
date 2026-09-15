"use client";

import { useState } from "react";
import Link from "next/link";

import AuthInput from "./AuthInput";

import PasswordInput from "./PasswordInput";
import AuthButton from "./AuthButton";
import { useAuth } from "@/providers/auth-provider";

export default function LoginForm() {
  const { login, loading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    setError("");

    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }

    if (!password.trim()) {
      setError("Please enter your password.");
      return;
    }

    try {
      await login(email, password);
    } catch (err: any) {
      setError(
        err?.message ||
          "Unable to sign in."
      );
    }
  }

  return (
    <div className="w-full max-w-sm">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-white">
          Welcome back
        </h1>

        <p className="mt-2 text-sm text-zinc-400">
          Sign in to continue your research.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-5"
      >
        <AuthInput
          id="email"
          label="Email"
          type="email"
          placeholder="you@company.com"
          autoComplete="email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-xs font-medium text-zinc-400">
              Password
            </label>

            <Link
              href="/forgot-password"
              className="text-xs text-blue-500 hover:text-blue-400"
            >
              Forgot Password?
            </Link>
          </div>

          <PasswordInput
            id="password"
            label=""
            placeholder="••••••••"
            autoComplete="current-password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
          />
        </div>

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <AuthButton
          type="submit"
          loading={loading}
        >
          Sign In
        </AuthButton>
      </form>

      <p className="mt-8 text-center text-sm text-zinc-400">
        Don't have an account?{" "}
        <Link
          href="/register"
          className="font-medium text-blue-500 hover:text-blue-400"
        >
          Create one
        </Link>
      </p>
    </div>
  );
}