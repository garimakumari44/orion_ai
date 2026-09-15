import AuthLayout from "@/components/auth/AuthLayout";

export default function VerifyEmailPage() {
  return (
    <AuthLayout>

      <div className="w-full max-w-sm">

        <h1 className="text-2xl font-semibold">
          Verify your email
        </h1>

        <p className="mt-2 text-text-muted">
          We've sent a verification email to your inbox.
        </p>

      </div>

    </AuthLayout>
  );
}