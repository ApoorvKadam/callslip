import type { ReactNode } from "react";
import type { Answer } from "../api";
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
}

export function AnswerView({ runId, answer, active, onHover, onChoose }: Props) {
  const activeN = active?.runId === runId ? active.n : null;
  const byNumber = new Map(answer.citations.map((c) => [c.number, c]));

  function renderFragment(f: Fragment, key: string): ReactNode {
    const text = bold(f.text, key);
    if (f.cites.length === 0) return <span key={key}>{text}</span>;
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
    const content = shown.map((f, j) => renderFragment(f, `${i}-${j}`));
    if (bullet) {
      items.push(<li key={`li-${i}`}>{content}</li>);
    } else {
      flush();
      blocks.push(<p key={`p-${i}`}>{content}</p>);
    }
  });
  flush();

  return <div className="answer">{blocks}</div>;
}
