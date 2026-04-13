"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export type ReviewerDecisionState = {
  error: string | null;
};

async function submitDecision(userId: string, approved: boolean, reason: string): Promise<void> {
  const response = await backendAuthenticatedFetch(`/users/${userId}/reviewer-approval`, {
    method: "PATCH",
    body: JSON.stringify({ approved, reason: reason || null }),
  });

  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }
}

export async function approveReviewerAction(formData: FormData): Promise<void> {
  const userId = String(formData.get("userId") ?? "");
  const reason = String(formData.get("reason") ?? "").trim();
  await submitDecision(userId, true, reason);
  revalidatePath("/dashboard/admin/reviewers");
  redirect("/dashboard/admin/reviewers?updated=1");
}

export async function rejectReviewerAction(formData: FormData): Promise<void> {
  const userId = String(formData.get("userId") ?? "");
  const reason = String(formData.get("reason") ?? "").trim();
  await submitDecision(userId, false, reason);
  revalidatePath("/dashboard/admin/reviewers");
  redirect("/dashboard/admin/reviewers?updated=1");
}
