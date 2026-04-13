"use server";

import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export type ProjectCreateState = {
  error: string | null;
};

export async function createProjectAction(
  _previousState: ProjectCreateState,
  formData: FormData,
): Promise<ProjectCreateState> {
  const payload = new FormData();
  payload.append("title", String(formData.get("title") ?? "").trim());
  payload.append("description", String(formData.get("description") ?? "").trim());

  const mentorEmail = String(formData.get("mentorEmail") ?? "").trim();
  if (mentorEmail) {
    payload.append("mentor_email", mentorEmail);
  }
  const sessionId = String(formData.get("sessionId") ?? "").trim();
  if (sessionId) {
    payload.append("session_id", sessionId);
  }

  for (const [inputName, outputName] of [
    ["paperFile", "paper_file"],
    ["slidesFile", "slides_file"],
    ["additionalFile", "additional_file"],
  ] as const) {
    const file = formData.get(inputName);
    if (file instanceof File && file.size > 0) {
      payload.append(outputName, file);
    }
  }

  const response = await backendAuthenticatedFetch("/projects", {
    method: "POST",
    body: payload,
  });
  if (!response.ok) {
    return { error: await parseBackendError(response) };
  }

  redirect("/dashboard/student/projects?created=1");
}
