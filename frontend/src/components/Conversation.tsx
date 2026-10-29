import { type FormEvent, type KeyboardEvent, useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  Check,
  CircleAlert,
  Columns2,
  CornerDownLeft,
  Download,
  LoaderCircle,
  Route,
} from "lucide-react";
import type { Answer, Run, SupportCheck } from "../api";
import type { CiteRef } from "../App";
import { answerMarkdown, download } from "../export";
import { count, seconds, shortCode } from "../format";
import { type AskMode, MODE_HELP } from "../modes";
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
  activity?: Activity[];
}

// One finished step of a running question, shown until its answer starts to appear.
export interface Activity {
  title: string;
  failed: boolean;
}

export interface PendingClarification {
  runId: string;
  toolUseId: string;
  question: string;
  options: string[];
}

const MODE_ICON = { agent: Route, baseline: ArrowRight, compare: Columns2 };
// The API refuses longer questions and replies; the box stops there.
const MAX_TEXT = 2000;

interface Props {
  mode: AskMode;
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
      {/* Only a finished answer: its citations and checks are then final. */}
      {run.answer && run.finished_at && (
        <button
          type="button"
          className="text-button export"
          onClick={() =>
            download(`callslip-answer-${run.id.slice(0, 8)}.md`, answerMarkdown(run, location.origin))
          }
        >
          <Download size={13} aria-hidden="true" />
          Export
        </button>
      )}
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
  // A reply to a clarifying question can go while the other half of a comparison still runs.
  const busy = sending || (!pending && runs.some((r) => r.status === "running"));
  // Both halves of one comparison: shown side by side instead of one after the other.
  const comparison =
    runs.length === 2 && !!runs[0].compare_id && runs[0].compare_id === runs[1].compare_id;
  const ModeIcon = MODE_ICON[props.mode];
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
              {(["agent", "baseline", "compare"] as const).map((m) => {
                const Icon = MODE_ICON[m];
                return (
                  <li key={m}>
                    <Icon size={16} aria-hidden="true" />
                    <span>{MODE_HELP[m]}</span>
                  </li>
                );
              })}
            </ul>
          </>
        )}

        {comparison && (
          <Comparison {...props} busy={busy} send={send} />
        )}
        {!comparison && runs.map((run) => (
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
            <Clarified run={run} />
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
              <Clarify pending={pending} busy={busy} send={send} onSkip={onSkip} />
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
            maxLength={MAX_TEXT}
          />
          <button type="submit" className="btn btn-primary" disabled={busy || !text.trim()}>
            {busy ? "Working" : pending ? "Reply" : "Ask"}
            {!busy && <CornerDownLeft size={15} aria-hidden="true" />}
          </button>
        </div>
        <p className="composer-hint meta">
          <span className="mode-help">
            <ModeIcon size={14} aria-hidden="true" />
            {MODE_HELP[props.mode]}
          </span>
          {text.length >= MAX_TEXT ? (
            <span className="limit-hint" role="status">
              The box stops at 2,000 characters.
            </span>
          ) : (
            <span className="keys-hint">Enter to send, Shift and Enter for a new line.</span>
          )}
        </p>
      </form>
    </>
  );
}

// Once the user has answered a clarifying question, the exchange keeps both, so the answer that
// follows reads in context.
function Clarified({ run }: { run: Run }) {
  if (!run.asked || !run.replied) return null;
  return (
    <div className="clarified">
      <p>
        <span className="label">Asked you</span> {run.asked}
      </p>
      <p>
        <span className="label">Your reply</span> {run.replied}
      </p>
    </div>
  );
}

function Clarify(props: {
  pending: PendingClarification;
  busy: boolean;
  send: (text: string) => Promise<void>;
  onSkip: () => void;
}) {
  const { pending, busy, send, onSkip } = props;
  return (
    <div className="clarify" role="group" aria-labelledby="clarify-question">
      <p id="clarify-question" className="clarify-question">
        {pending.question}
      </p>
      {pending.options.length > 0 && (
        <div className="options">
          {pending.options.map((o) => (
            <button key={o} type="button" className="btn" disabled={busy} onClick={() => void send(o)}>
              {o}
            </button>
          ))}
        </div>
      )}
      <button type="button" className="text-button" onClick={onSkip} disabled={busy}>
        Skip this question
      </button>
    </div>
  );
}

// One question asked both ways: the agent and the single pass side by side, then what differs.
function Comparison(
  props: Props & {
    busy: boolean;
    send: (text: string) => Promise<void>;
  },
) {
  const { runs, selectedId, pending, busy, send } = props;
  const ordered = [...runs].sort((a, b) => Number(b.mode === "agent") - Number(a.mode === "agent"));
  return (
    <article className="comparison" aria-labelledby="compare-question">
      <h2 id="compare-question" className="compare-question">
        {ordered[0].question}
      </h2>
      <CompareSummary
        runs={ordered.map((r) => ({ ...r, answer: props.live[r.id]?.answer ?? r.answer }))}
      />
      <div className="compare-grid">
        {ordered.map((run) => (
          <section
            key={run.id}
            className={`compare-col${run.id === selectedId ? " selected" : ""}`}
            aria-label={run.mode === "agent" ? "Agent" : "Single pass"}
          >
            <button type="button" className="compare-head" onClick={() => props.onSelect(run.id)}>
              {run.mode === "agent" ? (
                <Route size={15} aria-hidden="true" />
              ) : (
                <ArrowRight size={15} aria-hidden="true" />
              )}
              {run.mode === "agent" ? "Agent" : "Single pass"}
            </button>
            <RunMeta
              run={run}
              answer={props.live[run.id]?.answer ?? run.answer}
              onShowSteps={() => props.onShowSteps(run.id)}
            />
            <Clarified run={run} />
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
              <Clarify pending={pending} busy={busy} send={send} onSkip={props.onSkip} />
            )}
          </section>
        ))}
      </div>
    </article>
  );
}

// What differs, from what each run recorded: documents cited, sources, searches, time.
function CompareSummary({ runs }: { runs: Run[] }) {
  // Only once both runs are recorded as finished, so their counts are final.
  if (runs.some((r) => !r.answer || !r.finished_at)) return null;
  // Documents by id, named by their short title: two documents never merge into one.
  const docs = runs.map(
    (r) =>
      new Map(
        r.answer!.citations
          .filter((c) => c.document_id !== null)
          .map((c) => [c.document_id!, shortCode(c.title)] as const),
      ),
  );
  const [agent, single] = docs;
  const onlyAgent = [...agent].filter(([id]) => !single.has(id)).map(([, name]) => name);
  const onlySingle = [...single].filter(([id]) => !agent.has(id)).map(([, name]) => name);
  return (
    <div className="compare-summary meta" aria-label="How the two answers differ">
      <table>
        <thead>
          <tr>
            <th scope="col" />
            <th scope="col">Agent</th>
            <th scope="col">Single pass</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Documents cited</th>
            {docs.map((d, i) => (
              <td key={i}>{d.size ? [...d.values()].join(", ") : "none"}</td>
            ))}
          </tr>
          <tr>
            <th scope="row">Sources</th>
            {runs.map((r) => (
              <td key={r.id}>{r.answer!.citations.length}</td>
            ))}
          </tr>
          <tr>
            <th scope="row">Tool calls</th>
            {runs.map((r) => (
              <td key={r.id}>{r.tool_calls}</td>
            ))}
          </tr>
          <tr>
            <th scope="row">Answered in</th>
            {runs.map((r) => (
              <td key={r.id}>{r.answer!.answer_ms ? seconds(r.answer!.answer_ms) : "-"}</td>
            ))}
          </tr>
        </tbody>
      </table>
      {(onlyAgent.length > 0 || onlySingle.length > 0) && (
        <p>
          {onlyAgent.length > 0 && <>Only the agent cited {onlyAgent.join(", ")}. </>}
          {onlySingle.length > 0 && <>Only the single pass cited {onlySingle.join(", ")}.</>}
        </p>
      )}
    </div>
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
  if (live?.activity) return <Progress steps={live.activity} />;
  if (!live?.draft) return null;
  return <DraftAnswer runId={run.id} text={live.draft} />;
}

// What a running question has done so far, then what it is doing now. It starts at once, so
// there is something to read before the answer begins.
function Progress({ steps }: { steps: Activity[] }) {
  return (
    <ol className="progress" aria-live="polite">
      {steps.map((step, i) => (
        <li key={i} className={step.failed ? "failed" : undefined}>
          {step.failed ? (
            <CircleAlert size={14} aria-hidden="true" />
          ) : (
            <Check size={14} aria-hidden="true" />
          )}
          {step.title}
          {step.failed && ", failed"}
        </li>
      ))}
      <li className="now">
        <LoaderCircle size={14} aria-hidden="true" />
        {steps.length === 0 ? "Choosing where to look" : "Reading what it found"}
      </li>
    </ol>
  );
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

