import { type FormEvent, type KeyboardEvent, useState } from "react";
import type { Mode, Run } from "../api";
import { AnswerView } from "./AnswerView";

const STATUS_TEXT: Record<Run["status"], string> = {
  running: "Working…",
  needs_clarification: "Needs your answer",
  complete: "Answered",
  incomplete: "Incomplete",
  failed: "Failed",
  abandoned: "Skipped",
};

export interface PendingClarification {
  runId: string;
  toolUseId: string;
  question: string;
  options: string[];
}

interface Props {
  runs: Run[];
  selectedId: string | null;
  mode: Mode;
  onMode: (mode: Mode) => void;
  pending: PendingClarification | null;
  onSelect: (id: string) => void;
  onAsk: (text: string) => Promise<boolean>;
  onSkip: () => void;
  onNewSession: () => void;
  error: string | null;
}

export function Conversation(props: Props) {
  const { runs, selectedId, mode, onMode, pending, onSelect, onAsk, onSkip, onNewSession, error } =
    props;
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const busy = sending || runs.some((r) => r.status === "running");

  async function send(value: string) {
    const q = value.trim();
    if (!q || busy) return;
    setSending(true);
    try {
      // Keep the text when sending failed, so nothing typed is lost.
      if (await onAsk(q)) setText("");
    } finally {
      setSending(false);
    }
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    void send(text);
  }

  function onKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send(text);
    }
  }

  return (
    <section className="panel conversation" aria-labelledby="conversation-heading">
      <div className="panel-head">
        <h2 id="conversation-heading">Questions</h2>
        <button type="button" className="link-button" onClick={onNewSession}>
          New conversation
        </button>
      </div>

      {runs.length === 0 && (
        <p className="muted">
          Ask about the uploaded documents. Answers cite the document and page for every claim.
        </p>
      )}

      <ol className="runs">
        {runs.map((run) => (
          <li key={run.id} className={`run${run.id === selectedId ? " selected" : ""}`}>
            <button type="button" className="run-question" onClick={() => onSelect(run.id)}>
              <span>{run.question}</span>
              <span className="run-meta">
                <span className="muted small">{run.mode === "agent" ? "Agent" : "Single pass"}</span>
                <span className={`badge badge-run-${run.status}`}>{STATUS_TEXT[run.status]}</span>
              </span>
            </button>
            {run.status_reason && <p className="small muted">{run.status_reason}</p>}
            {run.answer && <AnswerView answer={run.answer} />}
          </li>
        ))}
      </ol>

      {pending && (
        <div className="clarify" role="group" aria-labelledby="clarify-question">
          <p id="clarify-question">
            <strong>The agent asks:</strong> {pending.question}
          </p>
          {pending.options.length > 0 && (
            <div className="options">
              {pending.options.map((o) => (
                <button key={o} type="button" disabled={busy} onClick={() => void send(o)}>
                  {o}
                </button>
              ))}
            </div>
          )}
          <button type="button" className="link-button" onClick={onSkip} disabled={busy}>
            Skip this question
          </button>
        </div>
      )}

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      <form className="composer" onSubmit={submit}>
        <label htmlFor="question" className="visually-hidden">
          {pending ? "Your reply" : "Your question"}
        </label>
        <textarea
          id="question"
          rows={3}
          value={text}
          placeholder={
            pending ? "Reply to the agent's question" : "Ask a question about the documents"
          }
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKey}
          maxLength={2000}
        />
        <div className="composer-actions">
          {!pending && (
            <fieldset className="mode">
              <legend className="visually-hidden">Answering mode</legend>
              <label>
                <input
                  type="radio"
                  name="mode"
                  checked={mode === "agent"}
                  onChange={() => onMode("agent")}
                />{" "}
                Agent
              </label>
              <label>
                <input
                  type="radio"
                  name="mode"
                  checked={mode === "baseline"}
                  onChange={() => onMode("baseline")}
                />{" "}
                Single pass
              </label>
            </fieldset>
          )}
          <button type="submit" disabled={busy || !text.trim()}>
            {busy ? "Working…" : pending ? "Reply" : "Ask"}
          </button>
        </div>
      </form>
    </section>
  );
}
