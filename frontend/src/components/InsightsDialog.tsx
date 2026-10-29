import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";
import { getInsights, type Insights } from "../api";

// How the viewer's own questions went over the last 30 days: outcomes, time, checked quotes,
// their ratings and the model cost. Only their conversations are counted; numbers only.
export function InsightsDialog({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [data, setData] = useState<Insights | null>(null);
  const [failed, setFailed] = useState<string | null>(null);

  // A modal dialog, like the page preview: Escape closes it and focus returns to the button.
  useEffect(() => {
    if (dialog.current && !dialog.current.open) dialog.current.showModal();
    getInsights()
      .then(setData)
      .catch((e) => setFailed(e instanceof Error ? e.message : String(e)));
  }, []);

  const rated = data ? data.useful + data.not_useful : 0;
  return (
    <dialog
      ref={dialog}
      className="page-preview insights"
      aria-labelledby="insights-title"
      onClose={onClose}
      onClick={(e) => {
        const box = dialog.current?.getBoundingClientRect();
        const outside =
          box &&
          (e.clientX < box.left ||
            e.clientX > box.right ||
            e.clientY < box.top ||
            e.clientY > box.bottom);
        if (e.target === dialog.current && outside) dialog.current?.close();
      }}
    >
      <header className="preview-head">
        <h2 id="insights-title">
          Your questions <span className="meta">last {data?.days ?? 30} days</span>
        </h2>
        <button
          type="button"
          className="icon-button"
          aria-label="Close"
          onClick={() => dialog.current?.close()}
        >
          <X size={16} aria-hidden="true" />
        </button>
      </header>
      {failed && (
        <p className="preview-status error" role="alert">
          Could not load your insights: {failed}
        </p>
      )}
      {!data && !failed && <p className="preview-status meta">Loading</p>}
      {data && data.runs === 0 && (
        <p className="preview-status">Nothing yet. Ask a question, and its outcome shows here.</p>
      )}
      {data && data.runs > 0 && (
        <dl className="insight-grid">
          <Stat label="Answers requested" value={data.runs} note="a comparison counts as two" />
          <Stat label="Answered" value={data.complete} />
          <Stat
            label="Incomplete or failed"
            value={data.incomplete + data.failed}
            note="stopped at a limit, interrupted, or an error"
          />
          <Stat label="Asked you to clarify" value={data.asked_to_clarify} />
          <Stat
            label="Typical time"
            value={data.median_ms === null ? "none" : `${(data.median_ms / 1000).toFixed(1)} s`}
            note="median of finished answers"
          />
          <Stat
            label="Quotes found on their page"
            value={`${data.citations_verified} of ${data.citations}`}
          />
          <Stat
            label="Rated useful"
            value={`${data.useful} of ${rated}`}
            note={`${data.rateable - rated} finished answers not rated`}
          />
          <Stat label="Model cost" value={`$${data.cost_usd.toFixed(4)}`} note="estimated" />
        </dl>
      )}
      <p className="preview-status meta">
        Only your own conversations are counted. Your questions and notes are never shown to
        anyone else.
      </p>
    </dialog>
  );
}

function Stat({ label, value, note }: { label: string; value: number | string; note?: string }) {
  return (
    <div className="insight">
      <dt className="meta">{label}</dt>
      <dd>
        <span className="insight-value">{value}</span>
        {note && <span className="meta">{note}</span>}
      </dd>
    </div>
  );
}
