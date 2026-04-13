"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function inviteTeamMemberAction(formData: FormData): Promise<void> {
  const projectId = String(formData.get("projectId") ?? "");
  const email = String(formData.get("email") ?? "").trim();

  const response = await backendAuthenticatedFetch(`/projects/${projectId}/team-invitations`, {
    method: "POST",
    body: JSON.stringify({ email }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  revalidatePath(`/dashboard/student/projects/${projectId}/team`);
  revalidatePath("/dashboard/student/projects");
  redirect(`/dashboard/student/projects/${projectId}/team?updated=1`);
}
