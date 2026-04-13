import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <section className="panel">
      <p className="eyebrow">Authentication</p>
      <h2>Sign in</h2>
      <LoginForm />
      <p>Google OAuth and secure session handling will connect through the FastAPI backend.</p>
    </section>
  );
}
