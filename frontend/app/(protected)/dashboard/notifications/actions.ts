"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { parseBackendError } from "@/lib/api";
import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function markNotificationReadAction(formData: FormData): Promise<void> {
  const notificationId = String(formData.get("notificationId") ?? "");
  const response = await backendAuthenticatedFetch(`/notifications/${notificationId}/read`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  revalidatePath("/dashboard/notifications");
  redirect("/dashboard/notifications?updated=1");
}

export async function markAllNotificationsReadAction(): Promise<void> {
  const response = await backendAuthenticatedFetch("/notifications/read-all", {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(await parseBackendError(response));
  }

  revalidatePath("/dashboard/notifications");
  redirect("/dashboard/notifications?updated=1");
}