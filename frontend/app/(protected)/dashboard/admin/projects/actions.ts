"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

async function submitDecision(projectId: string, approved: boolean, posterNumber: string, reason: string): Promise<void> {
  const response = await backendAuthenticatedFetch(`/projects/${projectId}/decision`, {
    method: "PATCH",
    body: JSON.stringify({
      approved,
      poster_number: posterNumber || null,
      reason: reason || null,
    }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }
}

export async function approveProjectAction(formData: FormData): Promise<void> {
  const projectId = String(formData.get("projectId") ?? "");
  const posterNumber = String(formData.get("posterNumber") ?? "").trim();
  const reason = String(formData.get("reason") ?? "").trim();
  await submitDecision(projectId, true, posterNumber, reason);
  revalidatePath("/dashboard/admin/projects");
  redirect("/dashboard/admin/projects?updated=1");
}

export async function rejectProjectAction(formData: FormData): Promise<void> {
  const projectId = String(formData.get("projectId") ?? "");
  const reason = String(formData.get("reason") ?? "").trim();
  await submitDecision(projectId, false, "", reason);
  revalidatePath("/dashboard/admin/projects");
  redirect("/dashboard/admin/projects?updated=1");
}
