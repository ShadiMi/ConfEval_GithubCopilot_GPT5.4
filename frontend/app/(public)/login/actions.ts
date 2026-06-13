"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { parseBackendError, parseRequestError } from "@/lib/api";
import { appConfig } from "@/lib/config";

export type LoginActionState = {
  error: string | null;
};

export async function loginAction(
  _previousState: LoginActionState,
  formData: FormData,
): Promise<LoginActionState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  let response: Response;

  try {
    response = await fetch(`${appConfig.backendUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
      cache: "no-store",
    });
  } catch (error) {
    return {
      error: parseRequestError(error, "Unable to reach the authentication service."),
    };
  }

  if (!response.ok) {
    return { error: await parseBackendError(response) };
  }

  let tokens: {
    access_token: string;
    refresh_token: string;
  };

  try {
    tokens = (await response.json()) as {
      access_token: string;
      refresh_token: string;
    };
  } catch (error) {
    return {
      error: parseRequestError(error, "Authentication service returned an invalid response."),
    };
  }

  const cookieStore = await cookies();
  const secure = process.env.NODE_ENV === "production";
  cookieStore.set("confeval_access_token", tokens.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure,
    path: "/",
    maxAge: 60 * 15,
  });
  cookieStore.set("confeval_refresh_token", tokens.refresh_token, {
    httpOnly: true,
    sameSite: "lax",
    secure,
    path: "/",
    maxAge: 60 * 60 * 24 * 14,
  });

  redirect("/dashboard");
}
