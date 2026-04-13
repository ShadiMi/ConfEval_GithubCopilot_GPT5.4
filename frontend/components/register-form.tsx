"use client";

import { useActionState, useState } from "react";

import { registerAction, type RegisterActionState } from "@/app/(public)/register/actions";

const roleOptions = [
  { value: "student", label: "Student" },
  { value: "internal_reviewer", label: "Internal Reviewer" },
  { value: "external_reviewer", label: "External Reviewer" },
];

const initialState: RegisterActionState = {
  error: null,
};

export function RegisterForm() {
  const [role, setRole] = useState("student");
  const [state, action, pending] = useActionState(registerAction, initialState);

  return (
    <form className="form" action={action} encType="multipart/form-data">
      <label>
        Full name
        <input name="fullName" type="text" placeholder="Researcher Name" required />
      </label>
      <label>
        Email
        <input name="email" type="email" placeholder="name@institution.edu" required />
      </label>
      <label>
        Password
        <input name="password" type="password" placeholder="At least 12 characters" required minLength={12} />
      </label>
      <label>
        Role
        <select name="role" value={role} onChange={(event) => setRole(event.target.value)}>
          {roleOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Affiliation
        <input name="affiliation" type="text" placeholder="Required for external reviewers" required={role === "external_reviewer"} />
      </label>
      {role === "external_reviewer" ? (
        <label>
          CV file
          <input name="cvFile" type="file" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" required />
        </label>
      ) : null}
      <label>
        Phone number
        <input name="phoneNumber" type="tel" placeholder="Optional" />
      </label>
      <label>
        ID number
        <input name="idNumber" type="text" inputMode="numeric" pattern="[0-9]{9}" placeholder="9 digits if provided" />
      </label>
      {state.error ? <p className="form-error">{state.error}</p> : null}
      <button type="submit" disabled={pending}>
        {pending ? "Creating account..." : "Create account"}
      </button>
    </form>
  );
}
