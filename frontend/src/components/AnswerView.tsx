import { type ReactNode, useState } from "react";
import { type Answer, type Citation, documentFileUrl } from "../api";

// Answers come back as plain text with light Markdown (paragraphs, "- " lists, **bold**).
// Citations are attached to text segments; they are rendered as numbered buttons in place.

const CITE = /\[\[cite:(\d+)\]\]|\*\*(.+?)\*\*/g;

function inline(text: string, onCite: (n: number) => void, key: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  for (const m of text.matchAll(CITE)) {
    if (m.index > last) out.push(text.slice(last, m.index));
    if (m[1]) {
      const n = Number(m[1]);
      out.push(
        <button
          key={`${key}-c${m.index}`}
          type="button"
          className="cite"
          aria-label={`Show source ${n}`}
          onClick={() => onCite(n)}
        >
          {n}
        </button>,
      );
    } else {
      out.push(<strong key={`${key}-b${m.index}`}>{m[2]}</strong>);
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

function renderText(answer: Answer, onCite: (n: number) => void): ReactNode[] {
  // Put citation markers right after the text they support, then lay out the lines:
  // consecutive "- " lines become one list, other lines become paragraphs.
  const marked = answer.segments
    .map((s) => s.text + s.citations.map((n) => `[[cite:${n}]]`).join(""))
    .join("");
  const out: ReactNode[] = [];
  let items: string[] = [];
  const flushList = () => {
    if (items.length === 0) return;
    const k = out.length;
    out.push(
      <ul key={k}>
        {items.map((item, j) => (
          <li key={j}>{inline(item, onCite, `${k}-${j}`)}</li>
        ))}
      </ul>,
    );
    items = [];
  };
  for (const line of marked.split("\n")) {
    if (!line.trim()) {
      flushList();
      continue;
    }
    const bullet = line.match(/^\s*[-*] (.*)$/);
    if (bullet) {
      items.push(bullet[1]);
      continue;
    }
    flushList();
    const k = out.length;
    out.push(<p key={k}>{inline(line.replace(/^#+\s*/, ""), onCite, String(k))}</p>);
  }
  flushList();
  return out;
}

function SourceCard({ c }: { c: Citation }) {
  const verified = c.provenance === "verified";
  return (
    <div className="source-card">
      <div className="source-head">
        <span className="cite static">{c.number}</span>
        <span className="source-title">{c.title}</span>
        <span className={`badge ${verified ? "badge-ready" : "badge-failed"}`}>
          {verified ? "Quote found on page" : `Check failed: ${c.provenance.replace(/_/g, " ")}`}
        </span>
      </div>
      <blockquote>{c.cited_text}</blockquote>
      {c.document_id !== null && c.page_no !== null && (
        <a href={documentFileUrl(c.document_id, c.page_no)} target="_blank" rel="noreferrer">
          Open page {c.page_no}
        </a>
      )}
    </div>
  );
}

export function AnswerView({ answer }: { answer: Answer }) {
  const [shown, setShown] = useState<number | null>(null);
  const selected = answer.citations.find((c) => c.number === shown);
  return (
    <div className="answer">
      <div className="answer-text">{renderText(answer, setShown)}</div>
      {answer.citations.length > 0 && (
        <p className="muted small">
          {answer.citations_verified} of {answer.citations.length} citations checked against the
          source page. Select a number to see the quote.
        </p>
      )}
      {selected && <SourceCard c={selected} />}
    </div>
  );
}
