"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function saveProjectAssignmentsAction(formData: FormData): Promise<void> {
  const projectId = String(formData.get("projectId") ?? "");
  const reviewerIds = formData.getAll("reviewerId").map((value) => String(value));

  const response = await backendAuthenticatedFetch(`/reviews/projects/${projectId}/assignments`, {
    method: "PUT",
    body: JSON.stringify({ reviewer_ids: reviewerIds }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  revalidatePath("/dashboard/admin/assignments");
  revalidatePath("/dashboard/reviewer/assignments");
  redirect("/dashboard/admin/assignments?updated=1");
}