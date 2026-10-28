import { type FormEvent, type KeyboardEvent, useEffect, useRef, useState } from "react";
import { ArrowRight, CornerDownLeft, Route } from "lucide-react";
import type { Answer, Mode, Run, SupportCheck } from "../api";
import type { CiteRef } from "../App";
import { count, seconds } from "../format";
import { MODE_HELP } from "../modes";
import { AnswerView } from "./AnswerView";

// Status words for runs that need attention; a plain answered run shows none.
const STATUS: Partial<Record<Run["status"], [string, string]>> = {
  running: ["Working", "mark"],
  needs_clarification: ["Waiting for your reply", "mark mark-wait"],
  incomplete: ["Incomplete", "mark mark-warn"],
  failed: ["Failed", "mark mark-bad"],
  abandoned: ["Skipped", "mark"],
};

// From a running question's events: the checked answer once it exists, or the text so far.
export interface LiveAnswer {
  answer?: Answer;
  draft?: string;
}

export interface PendingClarification {
  runId: string;
  toolUseId: string;
  question: string;
  options: string[];
}

interface Props {
  mode: Mode;
  runs: Run[];
  live: Record<string, LiveAnswer>;
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

function RunMeta(props: { run: Run; answer: Answer | null; onShowSteps: () => void }) {
  const { run, answer, onShowSteps } = props;
  // The answer shows while its quotes are still being checked, so "Working" would mislead.
  const checking =
    run.status === "running" && answer !== null && answer.citations.length > 0 && !answer.support;
  const status = checking ? undefined : STATUS[run.status];
  return (
    <div className="exchange-meta meta">
      <span>{run.mode === "agent" ? "Agent" : "Single pass"}</span>
      {status && <span className={status[1]}>{status[0]}</span>}
      {answer?.answer_ms ? (
        <span>Answered in {seconds(answer.answer_ms)}</span>
      ) : (
        run.exec_ms > 0 && <span>{seconds(run.exec_ms)} in total</span>
      )}
      {answer && answer.citations.length > 0 && (
        <span>
          {count(answer.citations.length, "source")}
          {answer.citations_verified === answer.citations.length
            ? ", every quote found on its page"
            : `, ${answer.citations.length - answer.citations_verified} not found on the page`}
        </span>
      )}
      {checking && <span className="mark">Checking quotes</span>}
      {answer?.support && answer.support.length > 0 && <SupportSummary checks={answer.support} />}
      <button type="button" className="text-button" onClick={onShowSteps}>
        {run.tool_calls > 0 ? `Steps (${run.tool_calls})` : "Steps"}
      </button>
    </div>
  );
}

// "4 of 5 cited sentences supported, 1 not checked", from the support check.
function SupportSummary({ checks }: { checks: SupportCheck[] }) {
  const unchecked = checks.filter((c) => c.verdict === "not_checked").length;
  if (unchecked === checks.length) return <span>support not checked</span>;
  const supported = checks.filter((c) => c.verdict === "supported").length;
  const label =
    `${supported} of ${count(checks.length, "cited sentence")} supported` +
    (unchecked ? `, ${unchecked} not checked` : "");
  return <span className={supported === checks.length ? undefined : "check-warn"}>{label}</span>;
}

export function Conversation(props: Props) {
  const { runs, selectedId, pending, onSelect, onAsk, onSkip, error } = props;
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const busy = sending || runs.some((r) => r.status === "running");
  const end = useRef<HTMLDivElement>(null);
  const transcript = useRef<HTMLDivElement>(null);

  // Keep the newest exchange in view as questions are added.
  useEffect(() => {
    end.current?.scrollIntoView({ block: "end" });
  }, [runs.length, pending?.runId]);

  // Follow an answer as it is written, unless the reader has scrolled up to read something else.
  const writing = Object.values(props.live).reduce((n, l) => n + (l.draft?.length ?? 0), 0);
  useEffect(() => {
    const box = transcript.current;
    if (!box || writing === 0) return;
    if (box.scrollHeight - box.scrollTop - box.clientHeight < 160) {
      end.current?.scrollIntoView({ block: "end" });
    }
  }, [writing]);

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
      <div className="transcript" ref={transcript}>
        {runs.length === 0 && (
          <>
            <p className="intro">Ask a question about the documents in the library.</p>
            <p className="meta">
              Answers cite their sources by document and page, and each cited quote is checked
              against its page.
            </p>
            <ul className="modes">
              <li>
                <Route size={16} aria-hidden="true" />
                <span>{MODE_HELP.agent}</span>
              </li>
              <li>
                <ArrowRight size={16} aria-hidden="true" />
                <span>{MODE_HELP.baseline}</span>
              </li>
            </ul>
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
            <RunMeta
              run={run}
              answer={props.live[run.id]?.answer ?? run.answer}
              onShowSteps={() => props.onShowSteps(run.id)}
            />
            {run.status_reason && run.status !== "complete" && (
              <p className="meta">{run.status_reason}</p>
            )}
            <RunAnswer
              run={run}
              live={props.live[run.id]}
              active={props.active}
              onHover={props.onHover}
              onChoose={props.onChoose}
            />
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
            {!busy && <CornerDownLeft size={15} aria-hidden="true" />}
          </button>
        </div>
        <p className="composer-hint meta">
          <span className="mode-help">
            {props.mode === "agent" ? (
              <Route size={14} aria-hidden="true" />
            ) : (
              <ArrowRight size={14} aria-hidden="true" />
            )}
            {MODE_HELP[props.mode]}
          </span>
          <span>Enter to send, Shift and Enter for a new line.</span>
        </p>
      </form>
    </>
  );
}

// The checked answer when there is one; while the model is still writing, its text so far,
// without citations (they are checked once the answer is complete).
interface RunAnswerProps {
  run: Run;
  live?: LiveAnswer;
  active: CiteRef | null;
  onHover: (ref: CiteRef | null) => void;
  onChoose: (ref: CiteRef) => void;
}

function RunAnswer({ run, live, ...props }: RunAnswerProps) {
  const answer = run.answer ?? live?.answer;
  if (answer) {
    return (
      <AnswerView
        runId={run.id}
        answer={answer}
        active={props.active}
        onHover={props.onHover}
        onChoose={props.onChoose}
      />
    );
  }
  if (!live?.draft) return null;
  return <DraftAnswer runId={run.id} text={live.draft} />;
}

// The answer as the model writes it, drawn like the final answer so nothing shifts when that
// arrives; it only lacks the citations, which come with the checked answer.
function DraftAnswer({ runId, text }: { runId: string; text: string }) {
  const shown = useSteadyText(text);
  const draft: Answer = {
    text: shown,
    segments: [{ text: shown, citations: [] }],
    citations: [],
    citations_verified: 0,
  };
  return (
    <AnswerView
      runId={runId}
      answer={draft}
      active={null}
      onHover={() => undefined}
      onChoose={() => undefined}
      streaming
    />
  );
}

// Streamed text arrives in bursts. Reveal it at a steady pace so it reads as it is written: the
// first piece shows at once, and a large backlog is caught up in a few frames, never trickled.
function useSteadyText(target: string): string {
  const [shown, setShown] = useState(target);
  const current = useRef(target);
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || current.current === "" || !target.startsWith(current.current)) {
      current.current = target;
      setShown(target);
      return;
    }
    let frame = 0;
    const step = () => {
      const backlog = target.length - current.current.length;
      if (backlog <= 0) return;
      const next = current.current.length + Math.max(2, Math.ceil(backlog / 8));
      current.current = target.slice(0, next);
      setShown(current.current);
      frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [target]);
  return shown;
}

