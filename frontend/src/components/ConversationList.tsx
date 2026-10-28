import type { SessionSummary } from "../api";
import { count } from "../format";

// "2:41 PM" for today, "Oct 27" before that.
function when(iso: string): string {
  const d = new Date(iso);
  return d.toDateString() === new Date().toDateString()
    ? d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })
    : d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

// Earlier conversations: this browser's, or, signed in, the account's from any browser.
export function ConversationList({
  items,
  currentId,
  onOpen,
}: {
  items: SessionSummary[];
  currentId: string | null;
  onOpen: (id: string) => void;
}) {
  if (items.length === 0) {
    return <p className="meta">No conversations yet. Each one you start is kept here.</p>;
  }
  return (
    <ul className="conv-list">
      {items.map((c) => (
        <li key={c.id}>
          <button
            type="button"
            className="conv"
            aria-current={c.id === currentId ? "true" : undefined}
            onClick={() => onOpen(c.id)}
          >
            <span className="conv-title">{c.title}</span>
            <span className="meta">
              {count(c.questions, "question")} · {when(c.last_at)}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
