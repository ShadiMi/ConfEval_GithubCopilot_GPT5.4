"use client";

import { useActionState } from "react";

import { loginAction, type LoginActionState } from "@/app/(public)/login/actions";

const initialState: LoginActionState = {
  error: null,
};

export function LoginForm() {
  const [state, action, pending] = useActionState(loginAction, initialState);

  return (
    <form className="form" action={action}>
      <label>
        Email
        <input name="email" type="email" placeholder="name@institution.edu" required />
      </label>
      <label>
        Password
        <input name="password" type="password" placeholder="At least 12 characters" required />
      </label>
      {state.error ? <p className="form-error">{state.error}</p> : null}
      <button type="submit" disabled={pending}>
        {pending ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}
