import AuthLayout from "@/components/auth/AuthLayout";

export default function ForgotPasswordPage() {
  return (
    <AuthLayout>

      <div className="w-full max-w-sm">

        <h1 className="text-2xl font-semibold">
          Forgot Password
        </h1>

        <p className="mt-2 text-text-muted">
          Enter your email address and we'll send you a password reset link.
        </p>

      </div>

    </AuthLayout>
  );
}