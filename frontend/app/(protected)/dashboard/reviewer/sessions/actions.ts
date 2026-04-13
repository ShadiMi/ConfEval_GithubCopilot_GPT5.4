"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function applyToSessionAction(formData: FormData): Promise<void> {
  const sessionId = String(formData.get("sessionId") ?? "");
  const coverMessage = String(formData.get("coverMessage") ?? "").trim();

  const response = await backendAuthenticatedFetch("/reviewer-applications", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      cover_message: coverMessage || null,
    }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  revalidatePath("/dashboard/reviewer/sessions");
  redirect("/dashboard/reviewer/sessions?applied=1");
}
