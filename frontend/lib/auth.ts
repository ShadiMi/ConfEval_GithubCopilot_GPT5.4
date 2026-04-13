import { cookies } from "next/headers";

export type SessionRole = "student" | "internal_reviewer" | "external_reviewer" | "admin";

export type SessionUser = {
  accessToken: string;
  role: SessionRole | null;
  userId: string | null;
};

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) {
      return null;
    }
    const payload = Buffer.from(parts[1], "base64url").toString("utf-8");
    return JSON.parse(payload) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export async function getSessionUser(): Promise<SessionUser> {
  const store = await cookies();
  const accessToken = store.get("confeval_access_token")?.value;
  if (!accessToken) {
    return { accessToken: "", role: null, userId: null };
  }

  const payload = decodeJwtPayload(accessToken);
  return {
    accessToken,
    role: (payload?.role as SessionRole | undefined) ?? null,
    userId: (payload?.sub as string | undefined) ?? null,
  };
}
