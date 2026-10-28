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
  private: boolean; // the signed-in user's own upload
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
      // A rejected field: FastAPI's first validation message, e.g. "String should have at least 10 characters".
      else if (Array.isArray(detail) && typeof detail[0]?.msg === "string") message = detail[0].msg;
    } catch {
      // Not JSON: keep the status text.
    }
    throw new ApiError(message, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

// The signed-in user's email, or null.
export function getAccount(): Promise<{ email: string | null }> {
  return request("/api/auth/me");
}

export function signIn(
  email: string,
  password: string,
  create: boolean,
): Promise<{ email: string }> {
  return request(create ? "/api/auth/register" : "/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function signOut(): Promise<void> {
  return request("/api/auth/logout", { method: "POST" });
}

export function listDocuments(): Promise<DocumentInfo[]> {
  return request("/api/documents");
}

export function uploadDocument(file: File): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  return request("/api/documents", { method: "POST", body: form });
}

// Delete one of your own uploads.
export function deleteDocument(id: number): Promise<void> {
  return request(`/api/documents/${id}`, { method: "DELETE" });
}

export function documentFileUrl(id: number, page?: number): string {
  return `/api/documents/${id}/file${page ? `#page=${page}` : ""}`;
}

// Sessions and runs ----------------------------------------------------------------------

export type RunStatus =
  | "running"
  | "needs_clarification"
  | "complete"
  | "incomplete"
  | "failed"
  | "abandoned";

export type Mode = "agent" | "baseline";

export interface Citation {
  number: number;
  source: string;
  title: string;
  document_id: number | null;
  page_no: number | null;
  cited_text: string;
  provenance: string;
}

// A second model call's ruling on one cited piece of the answer: do its quotes say what it says?
export interface SupportCheck {
  claim: number;
  citations: number[];
  verdict: "supported" | "partly" | "not_supported" | "not_checked";
  reason: string;
}

export interface Answer {
  text: string;
  segments: { text: string; citations: number[] }[];
  citations: Citation[];
  citations_verified: number;
  support?: SupportCheck[];
  answer_ms?: number; // time to answer, before the quotes are checked
}

export interface RunEvent {
  seq: number;
  type: string;
  data: Record<string, unknown>;
}

export interface Run {
  id: string;
  session_id: string;
  mode: Mode;
  question: string;
  status: RunStatus;
  status_reason: string | null;
  answer: Answer | null;
  model_turns: number;
  tool_calls: number;
  exec_ms: number;
  created_at: string;
  finished_at: string | null;
  events?: RunEvent[];
}

export interface Session {
  id: string;
  created_at: string;
  runs: Run[];
}

const json = { "Content-Type": "application/json" };

export function createSession(): Promise<{ id: string }> {
  return request("/api/sessions", { method: "POST" });
}

// One earlier conversation in the list: its first question, how many, and when last used.
export interface SessionSummary {
  id: string;
  title: string;
  questions: number;
  created_at: string;
  last_at: string;
}

export function listSessions(): Promise<SessionSummary[]> {
  return request("/api/sessions");
}

export function getSession(id: string): Promise<Session> {
  return request(`/api/sessions/${id}`);
}

export function ask(sessionId: string, question: string, mode: Mode): Promise<Run> {
  return request(`/api/sessions/${sessionId}/runs`, {
    method: "POST",
    headers: json,
    body: JSON.stringify({ question, mode }),
  });
}

export function getRun(id: string): Promise<Run> {
  return request(`/api/runs/${id}`);
}

export function runEventsUrl(id: string): string {
  return `/api/runs/${id}/events`;
}

export function resume(
  sessionId: string,
  runId: string,
  toolUseId: string,
  reply: string,
  idempotencyKey: string,
): Promise<Run> {
  return request(`/api/sessions/${sessionId}/runs/${runId}/resume`, {
    method: "POST",
    headers: json,
    body: JSON.stringify({ tool_use_id: toolUseId, idempotency_key: idempotencyKey, reply }),
  });
}

export function abandon(sessionId: string, runId: string): Promise<{ status: string }> {
  return request(`/api/sessions/${sessionId}/runs/${runId}/abandon`, { method: "POST" });
}
