import { RegisterForm } from "@/components/register-form";

export default function RegisterPage() {
  return (
    <section className="panel">
      <p className="eyebrow">Onboarding</p>
      <h2>Create an account</h2>
      <RegisterForm />
      <p>Reviewer accounts enter a pending approval state until an admin approves them.</p>
    </section>
  );
}
