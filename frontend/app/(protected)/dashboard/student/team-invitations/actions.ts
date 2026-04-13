"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

async function respond(token: string, accept: boolean): Promise<void> {
  const path = accept ? `/projects/team-invitations/${token}/accept` : `/projects/team-invitations/${token}/decline`;
  const response = await backendAuthenticatedFetch(path, { method: "POST" });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }
}

export async function acceptInvitationAction(formData: FormData): Promise<void> {
  await respond(String(formData.get("token") ?? ""), true);
  revalidatePath("/dashboard/student/team-invitations");
  revalidatePath("/dashboard/student/projects");
  redirect("/dashboard/student/team-invitations?updated=1");
}

export async function declineInvitationAction(formData: FormData): Promise<void> {
  await respond(String(formData.get("token") ?? ""), false);
  revalidatePath("/dashboard/student/team-invitations");
  redirect("/dashboard/student/team-invitations?updated=1");
}
