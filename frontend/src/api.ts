// Typed calls to the backend. Every request goes to the same origin; nginx forwards /api.

export type DocumentStatus = "queued" | "processing" | "ready" | "failed";

export interface DocumentInfo {
  id: number;
  title: string;
  filename: string;
  status: DocumentStatus;
  error: string | null;
  page_count: number | null;
  byte_size: number;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      const detail = body?.detail;
      if (typeof detail === "string") message = detail;
      else if (detail?.message) message = detail.message;
    } catch {
      // Not JSON: keep the status text.
    }
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}

export function listDocuments(): Promise<DocumentInfo[]> {
  return request("/api/documents");
}

export function uploadDocument(file: File): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  return request("/api/documents", { method: "POST", body: form });
}

export function documentFileUrl(id: number, page?: number): string {
  return `/api/documents/${id}/file${page ? `#page=${page}` : ""}`;
}
