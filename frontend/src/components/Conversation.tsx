import { type FormEvent, type KeyboardEvent, useEffect, useRef, useState } from "react";
import type { Run } from "../api";
import type { CiteRef } from "../App";
import { count, seconds } from "../format";
import { AnswerView } from "./AnswerView";

// Status words for runs that need attention; a plain answered run shows none.
const STATUS: Partial<Record<Run["status"], [string, string]>> = {
  running: ["Working", "mark"],
  needs_clarification: ["Waiting for your reply", "mark mark-wait"],
  incomplete: ["Incomplete", "mark mark-warn"],
  failed: ["Failed", "mark mark-bad"],
  abandoned: ["Skipped", "mark"],
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
  pending: PendingClarification | null;
  onSelect: (id: string) => void;
  onAsk: (text: string) => Promise<boolean>;
  onSkip: () => void;
  error: string | null;
  active: CiteRef | null;
  onHover: (ref: CiteRef | null) => void;
  onChoose: (ref: CiteRef) => void;
  onShowSteps: (runId: string) => void;
}

function RunMeta({ run, onShowSteps }: { run: Run; onShowSteps: () => void }) {
  const status = STATUS[run.status];
  const answer = run.answer;
  return (
    <div className="exchange-meta meta">
      <span>{run.mode === "agent" ? "Agent" : "Single pass"}</span>
      {status && <span className={status[1]}>{status[0]}</span>}
      {run.exec_ms > 0 && <span>{seconds(run.exec_ms)}</span>}
      {answer && answer.citations.length > 0 && (
        <span>
          {count(answer.citations.length, "source")}
          {answer.citations_verified === answer.citations.length
            ? ", every quote found on its page"
            : `, ${answer.citations.length - answer.citations_verified} not found on the page`}
        </span>
      )}
      <button type="button" className="text-button" onClick={onShowSteps}>
        {run.tool_calls > 0 ? `Steps (${run.tool_calls})` : "Steps"}
      </button>
    </div>
  );
}

export function Conversation(props: Props) {
  const { runs, selectedId, pending, onSelect, onAsk, onSkip, error } = props;
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const busy = sending || runs.some((r) => r.status === "running");
  const end = useRef<HTMLDivElement>(null);

  // Keep the newest exchange in view as questions are added.
  useEffect(() => {
    end.current?.scrollIntoView({ block: "end" });
  }, [runs.length, pending?.runId]);

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
    <>
      <div className="transcript">
        {runs.length === 0 && (
          <>
            <p className="intro">Ask a question about the documents on the left.</p>
            <p className="meta">
              Answers cite the document and page for every claim, and each quote is checked
              against the page before it is shown.
            </p>
          </>
        )}

        {runs.map((run) => (
          <article
            key={run.id}
            className={`exchange${run.id === selectedId ? " selected" : ""}`}
            aria-labelledby={`q-${run.id}`}
          >
            <h2>
              <button
                type="button"
                id={`q-${run.id}`}
                className="question"
                onClick={() => onSelect(run.id)}
              >
                {run.question}
              </button>
            </h2>
            <RunMeta run={run} onShowSteps={() => props.onShowSteps(run.id)} />
            {run.status_reason && run.status !== "complete" && (
              <p className="meta">{run.status_reason}</p>
            )}
            {run.answer && (
              <AnswerView
                runId={run.id}
                answer={run.answer}
                active={props.active}
                onHover={props.onHover}
                onChoose={props.onChoose}
              />
            )}
            {pending?.runId === run.id && (
              <div className="clarify" role="group" aria-labelledby="clarify-question">
                <p id="clarify-question" className="clarify-question">
                  {pending.question}
                </p>
                {pending.options.length > 0 && (
                  <div className="options">
                    {pending.options.map((o) => (
                      <button
                        key={o}
                        type="button"
                        className="btn"
                        disabled={busy}
                        onClick={() => void send(o)}
                      >
                        {o}
                      </button>
                    ))}
                  </div>
                )}
                <button type="button" className="text-button" onClick={onSkip} disabled={busy}>
                  Skip this question
                </button>
              </div>
            )}
          </article>
        ))}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <div ref={end} />
      </div>

      <form className="composer" onSubmit={submit}>
        <div className="composer-inner">
          <label htmlFor="question" className="visually-hidden">
            {pending ? "Your reply" : "Your question"}
          </label>
          <textarea
            id="question"
            rows={1}
            value={text}
            placeholder={pending ? "Or type your own reply" : "Ask about the documents"}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKey}
            maxLength={2000}
          />
          <button type="submit" className="btn btn-primary" disabled={busy || !text.trim()}>
            {busy ? "Working" : pending ? "Reply" : "Ask"}
          </button>
        </div>
        <p className="composer-hint meta">Enter to send, Shift and Enter for a new line.</p>
      </form>
    </>
  );
}
