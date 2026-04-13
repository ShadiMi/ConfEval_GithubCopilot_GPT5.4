"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function saveReviewAction(formData: FormData): Promise<void> {
  const projectId = String(formData.get("projectId") ?? "");
  const intent = String(formData.get("intent") ?? "draft");
  const overallComment = String(formData.get("overallComment") ?? "").trim();

  const criterionScores = Array.from(formData.entries())
    .filter(([key, value]) => key.startsWith("score:") && String(value).trim() !== "")
    .map(([key, value]) => ({
      criteria_id: key.replace("score:", ""),
      score: Number(value),
    }));

  const response = await backendAuthenticatedFetch(`/reviews/projects/${projectId}/me`, {
    method: "PUT",
    body: JSON.stringify({
      overall_comment: overallComment || null,
      criterion_scores: criterionScores,
      submit: intent === "submit",
    }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  revalidatePath("/dashboard/reviewer/assignments");
  revalidatePath(`/dashboard/reviewer/assignments/${projectId}`);
  revalidatePath(`/dashboard/student/projects/${projectId}/reviews`);
  redirect(`/dashboard/reviewer/assignments/${projectId}?updated=1`);
}