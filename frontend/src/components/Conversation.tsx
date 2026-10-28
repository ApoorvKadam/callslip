import { type FormEvent, type KeyboardEvent, useState } from "react";
import type { Run } from "../api";
import { AnswerView } from "./AnswerView";

const STATUS_TEXT: Record<Run["status"], string> = {
  running: "Working…",
  needs_clarification: "Needs your answer",
  complete: "Answered",
  incomplete: "Incomplete",
  failed: "Failed",
  abandoned: "Skipped",
};

interface Props {
  runs: Run[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onAsk: (question: string) => Promise<void>;
  onNewSession: () => void;
  error: string | null;
}

export function Conversation({ runs, selectedId, onSelect, onAsk, onNewSession, error }: Props) {
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const busy = sending || runs.some((r) => r.status === "running");

  async function submit(e?: FormEvent) {
    e?.preventDefault();
    const q = question.trim();
    if (!q || busy) return;
    setSending(true);
    try {
      await onAsk(q);
      setQuestion("");
    } finally {
      setSending(false);
    }
  }

  function onKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void submit();
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
              <span className={`badge badge-run-${run.status}`}>{STATUS_TEXT[run.status]}</span>
            </button>
            {run.status_reason && <p className="small muted">{run.status_reason}</p>}
            {run.answer && <AnswerView answer={run.answer} />}
          </li>
        ))}
      </ol>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      <form className="composer" onSubmit={(e) => void submit(e)}>
        <label htmlFor="question" className="visually-hidden">
          Your question
        </label>
        <textarea
          id="question"
          rows={3}
          value={question}
          placeholder="Ask a question about the documents"
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={onKey}
          maxLength={2000}
        />
        <button type="submit" disabled={busy || !question.trim()}>
          {busy ? "Working…" : "Ask"}
        </button>
      </form>
    </section>
  );
}
