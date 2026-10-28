import { useEffect } from "react";
import { type Citation, type Run, type RunEvent, documentFileUrl } from "../api";
import type { CiteRef } from "../App";
import { count, dollars, seconds, shortCode } from "../format";

// The selected question's sources and steps, side by side with the conversation.

export type RailTab = "sources" | "steps";

type Evidence = { document_id: number; title: string; page_no: number; excerpt: string };

const num = (v: unknown) => (typeof v === "number" ? v : 0);

interface Props {
  run: Run | null;
  events: RunEvent[];
  tab: RailTab;
  onTab: (tab: RailTab) => void;
  active: CiteRef | null;
  chosen: CiteRef | null;
  onHover: (ref: CiteRef | null) => void;
  onChoose: (ref: CiteRef) => void;
}

export function RunRail(props: Props) {
  const { run, events, tab, onTab } = props;
  const citations = run?.answer?.citations ?? [];
  const toolCalls = events.filter((e) => e.type === "tool_call").length;
  const working = run?.status === "running";

  return (
    <>
      <div className="tabs" role="tablist" aria-label="Selected question">
        <button
          type="button"
          role="tab"
          id="tab-sources"
          aria-controls="panel-sources"
          aria-selected={tab === "sources"}
          className="tab"
          onClick={() => onTab("sources")}
        >
          Sources <span className="meta">{citations.length || ""}</span>
        </button>
        <button
          type="button"
          role="tab"
          id="tab-steps"
          aria-controls="panel-steps"
          aria-selected={tab === "steps"}
          className="tab"
          onClick={() => onTab("steps")}
        >
          Steps{" "}
          <span className="meta">
            {toolCalls || ""}
            {working ? " · working" : ""}
          </span>
        </button>
      </div>
      {tab === "sources" ? (
        <div className="tab-panel" role="tabpanel" id="panel-sources" aria-labelledby="tab-sources">
          <Sources {...props} citations={citations} />
        </div>
      ) : (
        <div className="tab-panel" role="tabpanel" id="panel-steps" aria-labelledby="tab-steps">
          <Steps run={run} events={events} />
        </div>
      )}
    </>
  );
}

function Sources({
  run,
  citations,
  active,
  chosen,
  onHover,
  onChoose,
}: Props & { citations: Citation[] }) {
  // Bring the chosen source into view, inside the rail only.
  useEffect(() => {
    if (!chosen || chosen.runId !== run?.id) return;
    document
      .getElementById(`source-${chosen.runId}-${chosen.n}`)
      ?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [chosen, run?.id]);

  if (!run) return <p className="rail-empty">Ask a question to see its sources here.</p>;
  if (citations.length === 0) {
    return (
      <p className="rail-empty">
        {run.status === "running" ? "Sources appear when the answer arrives." : "No sources cited."}
      </p>
    );
  }
  const activeN = active?.runId === run.id ? active.n : null;
  return (
    <ol className="sources">
      {citations.map((c) => {
        const found = c.provenance === "verified";
        return (
          <li
            key={c.number}
            id={`source-${run.id}-${c.number}`}
            className={`source${activeN === c.number ? " active" : ""}`}
            onMouseEnter={() => onHover({ runId: run.id, n: c.number })}
            onMouseLeave={() => onHover(null)}
            onClick={() => onChoose({ runId: run.id, n: c.number })}
          >
            {/* The card is selectable by pointer anywhere; this button makes it reachable by
                keyboard too. Its click (Enter or Space) bubbles to the card's handler. */}
            <button
              type="button"
              className="source-head"
              aria-pressed={chosen?.runId === run.id && chosen.n === c.number}
              aria-label={`Source ${c.number}: ${shortCode(c.title)}, page ${c.page_no}`}
              onFocus={() => onHover({ runId: run.id, n: c.number })}
              onBlur={() => onHover(null)}
            >
              <span className="source-number">{c.number}</span>
              <span className="label">{shortCode(c.title)}</span>
              <span className="meta">page {c.page_no}</span>
            </button>
            <blockquote>{c.cited_text}</blockquote>
            <div className="source-foot meta">
              <span className={found ? "check-ok" : "check-bad"}>
                {found
                  ? `Quote found on page ${c.page_no}`
                  : `Not confirmed: ${c.provenance.replace(/_/g, " ")}`}
              </span>
              {c.document_id !== null && c.page_no !== null && (
                <a
                  href={documentFileUrl(c.document_id, c.page_no)}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(e) => e.stopPropagation()}
                >
                  Open page {c.page_no}
                </a>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}

// Group retrieved passages by document: "OMB M-25-21 p. 5, 6, 12; NIST AI 100-1 p. 25".
function wherePassages(evidence: Evidence[]): string {
  const pages = new Map<string, number[]>();
  for (const ev of evidence) {
    const code = shortCode(ev.title);
    const list = pages.get(code) ?? [];
    if (!list.includes(ev.page_no)) list.push(ev.page_no);
    pages.set(code, list);
  }
  return [...pages]
    .map(([code, list]) => `${code} p. ${list.sort((a, b) => a - b).join(", ")}`)
    .join("; ");
}

function ToolStep({ d }: { d: Record<string, unknown> }) {
  const tool = String(d.tool);
  const input = (d.input ?? {}) as Record<string, unknown>;
  const evidence = (d.evidence as Evidence[] | undefined) ?? [];
  const status = String(d.status);
  const retries = (d.retries as string[] | undefined) ?? [];

  let title = tool;
  let request: string | null = null;
  if (tool === "search_documents") {
    // Name the documents a filtered search was limited to, when its results show them all.
    const ids = (input.document_ids as number[] | undefined) ?? [];
    const docs = [...new Set(evidence.map((e) => shortCode(e.title)))];
    if (ids.length === 0) title = "Searched all documents";
    else if (docs.length === ids.length) title = `Searched ${docs.join(", ")}`;
    else title = `Searched ${count(ids.length, "document")}`;
    request = String(input.query ?? "");
  } else if (tool === "read_document_section") {
    const doc = evidence[0] ? shortCode(evidence[0].title) : `document ${input.document_id}`;
    title = `Read ${doc}, pages ${input.page_start} to ${input.page_end}`;
  } else if (tool === "list_documents") {
    title = "Listed the documents";
  }

  const marks: [string, string][] = [];
  if (retries.length > 0 && status === "ok") marks.push([`Retried after: ${retries[0]}`, "mark mark-warn"]);
  if (status === "no_results") marks.push(["Nothing found", "mark"]);
  if (status === "not_run") marks.push(["Not run", "mark"]);
  if (status === "invalid_input") marks.push(["Invalid input", "mark mark-bad"]);
  if (status === "error" || status === "timeout") {
    marks.push([`Failed after ${count(num(d.attempts), "attempt")}`, "mark mark-bad"]);
  }

  return (
    <li className="step">
      <div className="step-head">
        <span className="step-title">{title}</span>
        <span className="meta">{seconds(num(d.ms))}</span>
      </div>
      {request && <code>{request}</code>}
      <p className="step-detail">
        {evidence.length > 0 && tool === "search_documents"
          ? `${count(evidence.length, "passage")}: ${wherePassages(evidence)}`
          : String(d.summary ?? "")}
      </p>
      {(marks.length > 0 || Boolean(d.cache)) && (
        <div className="step-marks">
          {marks.map(([text, cls]) => (
            <span key={text} className={cls}>
              {text}
            </span>
          ))}
          {d.cache ? <span className="meta">cache {String(d.cache)}</span> : null}
        </div>
      )}
      {status !== "ok" && retries.length > 0 && (
        <p className="meta step-detail">{retries.join("; ")}</p>
      )}
    </li>
  );
}

function Step({ e }: { e: RunEvent }) {
  const d = e.data;
  switch (e.type) {
    case "run_started":
      return (
        <li className="step">
          <span className="meta">
            Question received, {d.mode === "agent" ? "agent" : "single pass"}
          </span>
        </li>
      );
    case "tool_call":
      return <ToolStep d={d} />;
    case "model_call":
      return (
        <li className="step step-model meta">
          Model turn {num(d.turn)}
          {d.model ? `, ${String(d.model)}` : ""}: {seconds(num(d.ms))},{" "}
          {num(d.input_tokens).toLocaleString("en-US")} in /{" "}
          {num(d.output_tokens).toLocaleString("en-US")} out tokens
          {num(d.cache_read_tokens)
            ? ` (${num(d.cache_read_tokens).toLocaleString("en-US")} cached)`
            : ""}
          , {dollars(num(d.cost_usd))}
        </li>
      );
    case "clarification":
      return (
        <li className="step">
          <div className="step-head">
            <span className="step-title">Asked you</span>
          </div>
          <p className="step-detail">{String(d.question)}</p>
        </li>
      );
    case "clarification_answered":
      return (
        <li className="step">
          <div className="step-head">
            <span className="step-title">You replied</span>
          </div>
          <p className="step-detail">{String(d.reply)}</p>
        </li>
      );
    case "limit":
      return (
        <li className="step">
          <div className="step-head">
            <span className="step-title">Limit reached</span>
            <span className="mark mark-warn">Stopping</span>
          </div>
          <p className="step-detail">{String(d.reason)}</p>
        </li>
      );
    case "answer":
      return (
        <li className="step">
          <div className="step-head">
            <span className="step-title">Answered</span>
          </div>
          <p className="step-detail">
            {count((d.citations as unknown[] | undefined)?.length ?? 0, "citation")},{" "}
            {num(d.citations_verified)} found on their pages
          </p>
        </li>
      );
    case "run_finished":
      return (
        <li className="step step-total">
          <div className="step-head">
            <span className="step-title">
              {d.status === "complete" ? "Finished" : `Finished: ${String(d.status)}`}
            </span>
            <span className="meta">{seconds(num(d.ms))}</span>
          </div>
          {typeof d.reason === "string" && d.reason && <p className="step-detail">{d.reason}</p>}
          <p className="meta step-detail">
            {count(num(d.model_calls), "model call")}, {count(num(d.tool_calls), "tool call")},{" "}
            {(num(d.input_tokens) + num(d.output_tokens)).toLocaleString("en-US")} tokens,{" "}
            {dollars(num(d.cost_usd))}
          </p>
        </li>
      );
    default:
      return null;
  }
}

function Steps({ run, events }: { run: Run | null; events: RunEvent[] }) {
  if (!run) return <p className="rail-empty">Ask a question to see each step the agent takes.</p>;
  return (
    <ol className="steps" aria-live="polite" aria-relevant="additions">
      {events.map((e) => (
        <Step key={e.seq} e={e} />
      ))}
    </ol>
  );
}
