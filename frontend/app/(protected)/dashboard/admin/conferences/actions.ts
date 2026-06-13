"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError, parseRequestError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export type ConferenceActionState = {
  error: string | null;
};

export async function createConferenceAction(
  _previousState: ConferenceActionState,
  formData: FormData,
): Promise<ConferenceActionState> {
  let response: Response;

  try {
    response = await backendAuthenticatedFetch("/conferences", {
      method: "POST",
      body: JSON.stringify({
        name: String(formData.get("name") ?? "").trim(),
        description: String(formData.get("description") ?? "").trim() || null,
        start_date: String(formData.get("startDate") ?? ""),
        end_date: String(formData.get("endDate") ?? ""),
        status: String(formData.get("status") ?? "draft"),
        building: String(formData.get("building") ?? "").trim() || null,
        floor: formData.get("floor") ? Number(formData.get("floor")) : null,
        room: formData.get("room") ? Number(formData.get("room")) : null,
        location_text: String(formData.get("locationText") ?? "").trim() || null,
      }),
    });
  } catch (error) {
    return {
      error: parseRequestError(error, "Unable to reach the conference service."),
    };
  }

  if (!response.ok) {
    return { error: await parseBackendError(response) };
  }

  revalidatePath("/dashboard/admin/conferences");
  redirect("/dashboard/admin/conferences?created=1");
}
