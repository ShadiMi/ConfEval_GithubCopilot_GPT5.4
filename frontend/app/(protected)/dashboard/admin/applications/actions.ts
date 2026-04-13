"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

async function decideApplication(applicationId: string, approved: boolean, decisionNotes: string): Promise<void> {
  const response = await backendAuthenticatedFetch(`/reviewer-applications/${applicationId}/decision`, {
    method: "PATCH",
    body: JSON.stringify({ approved, decision_notes: decisionNotes || null }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }
}

export async function approveApplicationAction(formData: FormData): Promise<void> {
  await decideApplication(
    String(formData.get("applicationId") ?? ""),
    true,
    String(formData.get("decisionNotes") ?? "").trim(),
  );
  revalidatePath("/dashboard/admin/applications");
  revalidatePath("/dashboard/admin/sessions");
  redirect("/dashboard/admin/applications?updated=1");
}

export async function rejectApplicationAction(formData: FormData): Promise<void> {
  await decideApplication(
    String(formData.get("applicationId") ?? ""),
    false,
    String(formData.get("decisionNotes") ?? "").trim(),
  );
  revalidatePath("/dashboard/admin/applications");
  redirect("/dashboard/admin/applications?updated=1");
}
