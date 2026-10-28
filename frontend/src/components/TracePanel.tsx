import { type Run, type RunEvent, documentFileUrl } from "../api";

// The execution trace: every step the run took, with inputs, results, timing and tokens.

type Evidence = { document_id: number; title: string; page_no: number; excerpt: string };

const num = (v: unknown) => (typeof v === "number" ? v : 0);

function Step({ e }: { e: RunEvent }) {
  const d = e.data;
  switch (e.type) {
    case "run_started":
      return (
        <li className="step">
          <div className="step-head">
            <strong>Question received</strong>
            <span className="muted small">{String(d.mode)}</span>
          </div>
        </li>
      );
    case "tool_call": {
      const evidence = (d.evidence as Evidence[] | undefined) ?? [];
      const ok = d.status === "ok";
      return (
        <li className="step">
          <div className="step-head">
            <strong>{String(d.tool)}</strong>
            <span className={`badge ${ok ? "badge-ready" : "badge-processing"}`}>
              {String(d.status).replace(/_/g, " ")}
            </span>
          </div>
          <code className="step-input">{JSON.stringify(d.input)}</code>
          <div className="muted small">
            {String(d.summary ?? "")} · {num(d.ms)} ms
            {d.cache ? ` · cache ${String(d.cache)}` : ""}
          </div>
          {typeof d.error === "string" && <p className="error small">{d.error}</p>}
          {evidence.length > 0 && (
            <ol className="evidence">
              {evidence.map((ev, i) => (
                <li key={i}>
                  <a href={documentFileUrl(ev.document_id, ev.page_no)} target="_blank" rel="noreferrer">
                    {ev.title}, p. {ev.page_no}
                  </a>
                  <span className="muted small"> {ev.excerpt}…</span>
                </li>
              ))}
            </ol>
          )}
        </li>
      );
    }
    case "model_call":
      return (
        <li className="step">
          <div className="step-head">
            <strong>Model turn {num(d.turn)}</strong>
            <span className="muted small">{String(d.stop_reason ?? "")}</span>
          </div>
          <div className="muted small">
            {num(d.ms)} ms · {num(d.input_tokens)} in / {num(d.output_tokens)} out tokens
            {num(d.cache_read_tokens) ? ` · ${num(d.cache_read_tokens)} cached` : ""} · $
            {num(d.cost_usd).toFixed(4)}
          </div>
        </li>
      );
    case "answer":
      return (
        <li className="step">
          <div className="step-head">
            <strong>Answer</strong>
            <span className="muted small">
              {num(d.citations_verified)} of {(d.citations as unknown[] | undefined)?.length ?? 0}{" "}
              citations verified
            </span>
          </div>
        </li>
      );
    case "run_finished":
      return (
        <li className="step final">
          <div className="step-head">
            <strong>Finished: {String(d.status)}</strong>
          </div>
          {typeof d.reason === "string" && d.reason && <p className="small">{d.reason}</p>}
          <div className="muted small">
            {num(d.ms)} ms · {num(d.model_calls)} model calls · {num(d.tool_calls)} tool calls ·{" "}
            {num(d.input_tokens) + num(d.output_tokens)} tokens · ${num(d.cost_usd).toFixed(4)}
          </div>
        </li>
      );
    default:
      return (
        <li className="step">
          <strong>{e.type}</strong>
        </li>
      );
  }
}

export function TracePanel({ run, events }: { run: Run | null; events: RunEvent[] }) {
  return (
    <section className="panel" aria-labelledby="trace-heading">
      <div className="panel-head">
        <h2 id="trace-heading">Execution trace</h2>
        {run && <span className="muted small">{run.status.replace(/_/g, " ")}</span>}
      </div>
      {!run && <p className="muted">Ask a question to see each step here.</p>}
      <ol className="steps" aria-live="polite" aria-relevant="additions">
        {events.map((e) => (
          <Step key={e.seq} e={e} />
        ))}
      </ol>
    </section>
  );
}
