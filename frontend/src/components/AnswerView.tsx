import type { ReactNode } from "react";
import type { Answer, Citation } from "../api";
import type { CiteRef } from "../App";
import { shortCode } from "../format";

// Answers arrive as segments: a piece of text plus the numbers of the sources that support it.
// Text uses light Markdown (paragraphs, "- " lists, **bold**). Each supported piece is wrapped
// so that hovering it, or its number, highlights the piece and its source card together.

interface Fragment {
  text: string;
  cites: number[]; // the segment's citations
  last: boolean; // the segment's final fragment: its citation numbers follow it
}

function bold(text: string, key: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  for (const m of text.matchAll(/\*\*(.+?)\*\*/g)) {
    if (m.index > last) out.push(text.slice(last, m.index));
    out.push(<strong key={`${key}-${m.index}`}>{m[1]}</strong>);
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

// Letters and digits only (in any script), so the line-break hyphens and spacing of PDF text
// do not matter. A separator between two digits is kept, so "1.5" never matches "15".
const squash = (s: string) =>
  s
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, (sep, at: number, all: string) =>
      /\p{N}/u.test(all[at - 1] ?? "") && /\p{N}/u.test(all[at + sep.length] ?? "")
        ? sep.trim() || " "
        : "",
    );

// The model often copies a sentence from a source into its answer. Such text is shown in
// quotation marks, so the reader can tell the document's words from the answer's. Text the
// model already put in quotation marks, or shorter than eight words, is left as it is.
function copied(text: string, before: string, after: string, sources: Citation[]): boolean {
  if (/["“]\s*$/.test(before) || /^\s*["”]/.test(after) || /^["“]/.test(text)) return false;
  if (text.split(/\s+/).length < 8) return false;
  const t = squash(text);
  return t.length > 0 && sources.some((c) => squash(c.cited_text).includes(t));
}

// Split the segments into lines of fragments, keeping each fragment's citations.
function lines(answer: Answer): Fragment[][] {
  const out: Fragment[][] = [[]];
  for (const seg of answer.segments) {
    const parts = seg.text.split("\n");
    parts.forEach((text, i) => {
      if (i > 0) out.push([]);
      out[out.length - 1].push({ text, cites: seg.citations, last: i === parts.length - 1 });
    });
  }
  return out;
}

interface Props {
  runId: string;
  answer: Answer;
  active: CiteRef | null;
  onHover: (ref: CiteRef | null) => void;
  onChoose: (ref: CiteRef) => void;
  streaming?: boolean; // text still being written: no citations yet
}

export function AnswerView({ runId, answer, active, onHover, onChoose, streaming }: Props) {
  const activeN = active?.runId === runId ? active.n : null;
  const byNumber = new Map(answer.citations.map((c) => [c.number, c]));

  function renderFragment(f: Fragment, key: string, before: string, after: string): ReactNode {
    if (f.cites.length === 0) return <span key={key}>{bold(f.text, key)}</span>;
    const sources = f.cites.flatMap((n) => byNumber.get(n) ?? []);
    const [, lead, core, trail] = /^(\s*)([\s\S]*?)(\s*)$/.exec(f.text) ?? ["", "", f.text, ""];
    const quoted = copied(core, before, after, sources);
    const text = bold(quoted ? `${lead}“${core}”${trail}` : f.text, key);
    const isActive = activeN !== null && f.cites.includes(activeN);
    return (
      <span key={key}>
        <span
          className={`cited${isActive ? " active" : ""}`}
          onMouseEnter={() => onHover({ runId, n: f.cites[0] })}
          onMouseLeave={() => onHover(null)}
        >
          {text}
        </span>
        {f.last &&
          f.cites.map((n) => {
            const c = byNumber.get(n);
            const where = c ? `${shortCode(c.title)}, page ${c.page_no}` : "";
            return (
              <button
                key={`${key}-c${n}`}
                type="button"
                className={`cite${activeN === n ? " active" : ""}`}
                aria-label={`Source ${n}: ${where}`}
                onMouseEnter={() => onHover({ runId, n })}
                onMouseLeave={() => onHover(null)}
                onFocus={() => onHover({ runId, n })}
                onBlur={() => onHover(null)}
                onClick={() => onChoose({ runId, n })}
              >
                {n}
              </button>
            );
          })}
      </span>
    );
  }

  // Lay out the lines: consecutive "- " lines become one list, other lines paragraphs.
  const blocks: ReactNode[] = [];
  let items: ReactNode[] = [];
  const flush = () => {
    if (items.length) blocks.push(<ul key={`ul-${blocks.length}`}>{items}</ul>);
    items = [];
  };
  lines(answer).forEach((frags, i) => {
    const text = frags.map((f) => f.text).join("");
    if (!text.trim()) {
      flush();
      return;
    }
    const bullet = /^\s*[-*] /.exec(text);
    const heading = /^#+\s*/.exec(text);
    const strip = bullet?.[0].length ?? heading?.[0].length ?? 0;
    // Remove the list or heading marker from the first fragment(s).
    let left = strip;
    const shown = frags.map((f) => {
      if (left <= 0) return f;
      const cut = Math.min(left, f.text.length);
      left -= cut;
      return { ...f, text: f.text.slice(cut) };
    });
    const content = shown.map((f, j) =>
      renderFragment(f, `${i}-${j}`, shown[j - 1]?.text ?? "", shown[j + 1]?.text ?? ""),
    );
    if (bullet) {
      items.push(<li key={`li-${i}`}>{content}</li>);
    } else {
      flush();
      blocks.push(<p key={`p-${i}`}>{content}</p>);
    }
  });
  flush();

  return (
    <div className={`answer${streaming ? " streaming" : ""}`} aria-busy={streaming || undefined}>
      {blocks}
    </div>
  );
}
