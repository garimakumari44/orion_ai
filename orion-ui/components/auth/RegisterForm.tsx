"use client";

import { useState } from "react";
import Link from "next/link";

import AuthInput from "./AuthInput";
import PasswordInput from "./PasswordInput";
import AuthButton from "./AuthButton";

import { useAuth } from "@/providers/auth-provider";

export default function RegisterForm() {
  const { register, loading } = useAuth();

  const [full_name, setFull_name] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState("");

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    setError("");

    if (!full_name.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }

    if (!password.trim()) {
      setError("Please enter a password.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      await register({
        full_name,
        email,
        password,
      });
    } catch (err: any) {
      setError(
        err?.message ??
          "Unable to create your account."
      );
    }
  }

  return (
    <div className="w-full max-w-sm">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-white">
          Create your account
        </h1>

        <p className="mt-2 text-sm text-zinc-400">
          Start running institutional-grade research in minutes.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-5"
      >
        <AuthInput
          id="name"
          label="Full Name"
          type="text"
          placeholder="Jane Analyst"
          autoComplete="name"
          value={full_name}
          onChange={(e) =>
            setFull_name(e.target.value)
          }
        />

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

        <PasswordInput
          id="password"
          label="Password"
          placeholder="Create a password"
          autoComplete="new-password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <PasswordInput
          id="confirm-password"
          label="Confirm Password"
          placeholder="Confirm your password"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(e) =>
            setConfirmPassword(e.target.value)
          }
        />

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <AuthButton
          type="submit"
          loading={loading}
        >
          Create Account
        </AuthButton>
      </form>

      <p className="mt-8 text-center text-sm text-zinc-400">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-medium text-blue-500/60 hover:text-blue-400/60"
        >
          Sign In
        </Link>
      </p>
    </div>
  );
}