"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function createSessionAction(formData: FormData): Promise<void> {
  const criteria = [
    {
      name: String(formData.get("criteriaName") ?? "").trim(),
      description: String(formData.get("criteriaDescription") ?? "").trim() || null,
      max_score: Number(formData.get("criteriaMaxScore") ?? 100),
      weight: Number(formData.get("criteriaWeight") ?? 1),
      display_order: 0,
    },
  ];

  const tagIds = formData.getAll("tagIds").map((value) => String(value));
  const conferenceId = String(formData.get("conferenceId") ?? "").trim();
  const response = await backendAuthenticatedFetch("/conferences/sessions", {
    method: "POST",
    body: JSON.stringify({
      conference_id: conferenceId || null,
      name: String(formData.get("name") ?? "").trim(),
      description: String(formData.get("description") ?? "").trim() || null,
      start_date: String(formData.get("startDate") ?? ""),
      end_date: String(formData.get("endDate") ?? ""),
      status: String(formData.get("status") ?? "upcoming"),
      location_text: String(formData.get("locationText") ?? "").trim(),
      max_project_capacity: Number(formData.get("maxProjectCapacity") ?? 10),
      reviewers_per_project: Number(formData.get("reviewersPerProject") ?? 2),
      tag_ids: tagIds,
      criteria,
    }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }
  revalidatePath("/dashboard/admin/sessions");
  redirect("/dashboard/admin/sessions?created=1");
}
