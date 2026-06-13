export type BackendErrorPayload = {
  detail?: string;
};

export function parseRequestError(error: unknown, fallbackMessage: string): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return fallbackMessage;
}

export async function parseBackendError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as BackendErrorPayload;
    if (typeof data.detail === "string" && data.detail.length > 0) {
      return data.detail;
    }
  } catch {
    return `Request failed with status ${response.status}`;
  }

  return `Request failed with status ${response.status}`;
}
