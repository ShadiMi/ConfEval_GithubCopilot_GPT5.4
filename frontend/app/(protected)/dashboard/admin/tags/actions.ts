"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function createTagAction(formData: FormData): Promise<void> {
  const response = await backendAuthenticatedFetch("/tags", {
    method: "POST",
    body: JSON.stringify({
      name: String(formData.get("name") ?? "").trim(),
      description: String(formData.get("description") ?? "").trim() || null,
    }),
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }
  revalidatePath("/dashboard/admin/tags");
  redirect("/dashboard/admin/tags?created=1");
}
