"use server";

import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { appConfig } from "@/lib/config";

export type RegisterActionState = {
  error: string | null;
};

export async function registerAction(
  _previousState: RegisterActionState,
  formData: FormData,
): Promise<RegisterActionState> {
  const fullName = String(formData.get("fullName") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const role = String(formData.get("role") ?? "student");
  const affiliation = String(formData.get("affiliation") ?? "").trim();
  const phoneNumber = String(formData.get("phoneNumber") ?? "").trim();
  const idNumber = String(formData.get("idNumber") ?? "").trim();
  const cvFile = formData.get("cvFile");

  const response =
    role === "external_reviewer"
      ? await fetch(`${appConfig.backendUrl}/auth/register/external-reviewer`, {
          method: "POST",
          body: (() => {
            const payload = new FormData();
            payload.append("full_name", fullName);
            payload.append("email", email);
            payload.append("password", password);
            payload.append("affiliation", affiliation);
            if (phoneNumber) {
              payload.append("phone_number", phoneNumber);
            }
            if (idNumber) {
              payload.append("id_number", idNumber);
            }
            if (cvFile instanceof File) {
              payload.append("cv_file", cvFile);
            }
            return payload;
          })(),
          cache: "no-store",
        })
      : await fetch(`${appConfig.backendUrl}/auth/register`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            full_name: fullName,
            email,
            password,
            role,
            affiliation: affiliation || null,
            phone_number: phoneNumber || null,
            id_number: idNumber || null,
          }),
          cache: "no-store",
        });

  if (!response.ok) {
    return { error: await parseBackendError(response) };
  }

  if (role === "student") {
    redirect("/login?registered=1");
  }

  redirect("/pending-approval?registered=1");
}
