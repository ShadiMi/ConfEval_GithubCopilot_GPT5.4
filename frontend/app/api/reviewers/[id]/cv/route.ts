import { NextRequest, NextResponse } from "next/server";

import { backendAuthenticatedFetch } from "@/lib/server-api";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const response = await backendAuthenticatedFetch(`/users/${id}/cv`, {
    method: "GET",
  });

  if (!response.ok) {
    const message = await response.text();
    return NextResponse.json({ detail: message || "Unable to fetch CV" }, { status: response.status });
  }

  const headers = new Headers();
  const contentType = response.headers.get("content-type");
  const disposition = response.headers.get("content-disposition");
  if (contentType) {
    headers.set("content-type", contentType);
  }
  if (disposition) {
    headers.set("content-disposition", disposition);
  }

  return new NextResponse(response.body, {
    status: response.status,
    headers,
  });
}
