import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiError,
  type Mode,
  type Run,
  type RunEvent,
  type RunStatus,
  abandon,
  ask,
  createSession,
  getRun,
  getSession,
  resume,
  runEventsUrl,
} from "./api";
import { Conversation, type PendingClarification } from "./components/Conversation";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { RunRail, type RailTab } from "./components/RunRail";

const SESSION_KEY = "callslip.session";
const EVENT_TYPES = [
  "run_started",
  "tool_call",
  "model_call",
  "limit",
  "clarification",
  "clarification_answered",
  "answer",
  "run_finished",
];

// A citation in one run's answer: hovering highlights it, selecting also opens it in Sources.
export interface CiteRef {
  runId: string;
  n: number;
}

function errorText(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [events, setEvents] = useState<Record<string, RunEvent[]>>({});
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const lastReply = useRef<{ toolUseId: string; text: string; key: string } | null>(null);
  const [mode, setMode] = useState<Mode>("agent");
  const [tab, setTab] = useState<RailTab>("sources");
  const [hovered, setHovered] = useState<CiteRef | null>(null);
  const [chosen, setChosen] = useState<CiteRef | null>(null);
  const streams = useRef<Record<string, EventSource>>({});

  const replaceRun = useCallback((run: Run) => {
    setRuns((all) => all.map((r) => (r.id === run.id ? { ...r, ...run } : r)));
    if (run.events) setEvents((all) => ({ ...all, [run.id]: run.events! }));
  }, []);

  const refreshRun = useCallback(
    async (id: string) => replaceRun(await getRun(id)),
    [replaceRun],
  );

  // Follow a run's steps live. Events carry stable ids, so duplicates are dropped.
  const follow = useCallback(
    (id: string) => {
      if (streams.current[id]) return;
      const source = new EventSource(runEventsUrl(id));
      streams.current[id] = source;
      const add = (type: string) => (msg: MessageEvent) => {
        const seq = Number(msg.lastEventId);
        setEvents((all) => {
          const list = all[id] ?? [];
          if (list.some((e) => e.seq === seq)) return all;
          return { ...all, [id]: [...list, { seq, type, data: JSON.parse(msg.data) }] };
        });
      };
      EVENT_TYPES.forEach((t) => source.addEventListener(t, add(t)));
      source.addEventListener("end", (msg: MessageEvent) => {
        source.close();
        delete streams.current[id];
        // Take the final status from the stream at once, then read the finished run; a failed
        // read is retried, so the question never stays "Working" because of one lost request.
        const { status } = JSON.parse(msg.data) as { status: RunStatus };
        setRuns((all) => all.map((r) => (r.id === id ? { ...r, status } : r)));
        void (async () => {
          for (const delay of [0, 1000, 3000, 9000]) {
            await new Promise((done) => setTimeout(done, delay));
            try {
              await refreshRun(id);
              return;
            } catch {
              // try again
            }
          }
          setError("Could not load the finished answer. Reload the page to see it.");
        })();
      });
    },
    [refreshRun],
  );

  const startSession = useCallback(async () => {
    const { id } = await createSession();
    localStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
    setRuns([]);
    setEvents({});
    setSelectedId(null);
  }, []);

  // Restore the last session in this browser, or start a new one.
  useEffect(() => {
    const saved = localStorage.getItem(SESSION_KEY);
    (async () => {
      try {
        if (saved) {
          const session = await getSession(saved);
          setSessionId(session.id);
          setRuns(session.runs);
          const last = session.runs.at(-1);
          if (last) {
            setSelectedId(last.id);
            if (last.status === "running") follow(last.id);
            else await refreshRun(last.id);
          }
          return;
        }
      } catch (e) {
        // Only an unknown or expired session starts afresh. Any other failure keeps the saved
        // conversation, so a brief outage does not replace it.
        if (!(e instanceof ApiError && e.status === 404)) {
          setError(`Could not load the saved conversation: ${errorText(e)}. Reload to try again.`);
          return;
        }
      }
      try {
        await startSession();
      } catch (e) {
        setError(`Could not start a session: ${errorText(e)}`);
      }
    })();
  }, [follow, refreshRun, startSession]);

  // A run waiting for the user's reply, and the question it asked (from its last event).
  const waiting = runs.find((r) => r.status === "needs_clarification");
  const asked = waiting
    ? (events[waiting.id] ?? []).filter((e) => e.type === "clarification").at(-1)
    : undefined;
  const pending: PendingClarification | null =
    waiting && asked
      ? {
          runId: waiting.id,
          toolUseId: String(asked.data.tool_use_id),
          question: String(asked.data.question),
          options: (asked.data.options as string[]) ?? [],
        }
      : null;

  async function onAsk(text: string): Promise<boolean> {
    if (!sessionId) return false;
    setError(null);
    try {
      if (pending) {
        // Sending the same reply again (after a lost response) reuses its key, so the server
        // recognises the retry instead of reporting that the question is no longer waiting.
        const last = lastReply.current;
        const key =
          last && last.toolUseId === pending.toolUseId && last.text === text
            ? last.key
            : crypto.randomUUID();
        lastReply.current = { toolUseId: pending.toolUseId, text, key };
        const run = await resume(sessionId, pending.runId, pending.toolUseId, text, key);
        replaceRun(run);
        follow(run.id);
      } else {
        const run = await ask(sessionId, text, mode);
        setRuns((all) => [...all, run]);
        setSelectedId(run.id);
        setTab("steps"); // a new question: watch the agent work
        follow(run.id);
      }
      return true;
    } catch (e) {
      setError(errorText(e));
      // 409 on a reply: the run has moved on (an earlier reply may have been accepted while its
      // response was lost), so show the run as it is instead of the stale question.
      if (pending && e instanceof ApiError && e.status === 409) {
        await refreshRun(pending.runId).catch(() => undefined);
        follow(pending.runId);
      }
      return false;
    }
  }

  async function onSkip() {
    if (!sessionId || !pending) return;
    try {
      await abandon(sessionId, pending.runId);
      await refreshRun(pending.runId);
    } catch (e) {
      setError(errorText(e));
    }
  }

  async function onSelect(id: string) {
    setSelectedId(id);
    if (!events[id]) await refreshRun(id);
  }

  function onChoose(ref: CiteRef) {
    setChosen(ref);
    setTab("sources");
    if (ref.runId !== selectedId) void onSelect(ref.runId);
  }

  async function onNewSession() {
    setError(null);
    try {
      await startSession();
      setChosen(null);
      setHovered(null);
    } catch (e) {
      setError(`Could not start a new conversation: ${errorText(e)}`);
    }
  }

  const selected = runs.find((r) => r.id === selectedId) ?? null;

  const active = hovered ?? chosen;

  return (
    <div className="app">
      <header className="bar">
        <span className="wordmark">Callslip</span>
        <div className="bar-actions">
          <fieldset className="segmented" disabled={!!pending}>
            <legend className="visually-hidden">Answering mode</legend>
            <label>
              <input
                type="radio"
                name="mode"
                checked={mode === "agent"}
                onChange={() => setMode("agent")}
              />
              Agent
            </label>
            <label>
              <input
                type="radio"
                name="mode"
                checked={mode === "baseline"}
                onChange={() => setMode("baseline")}
              />
              Single pass
            </label>
          </fieldset>
          <button type="button" className="btn" onClick={() => void onNewSession()}>
            New conversation
          </button>
        </div>
      </header>
      <div className="layout">
        <aside className="docs" aria-label="Documents">
          <DocumentsPanel />
        </aside>
        <main className="talk">
          <Conversation
            runs={runs}
            selectedId={selectedId}
            onSelect={(id) => void onSelect(id)}
            onAsk={onAsk}
            pending={pending}
            onSkip={() => void onSkip()}
            error={error}
            active={active}
            onHover={setHovered}
            onChoose={onChoose}
            onShowSteps={(id) => {
              setTab("steps");
              void onSelect(id);
            }}
          />
        </main>
        <aside className="rail" aria-label="Sources and steps">
          <RunRail
            run={selected}
            events={selected ? (events[selected.id] ?? []) : []}
            tab={tab}
            onTab={setTab}
            active={active}
            chosen={chosen}
            onHover={setHovered}
            onChoose={onChoose}
          />
        </aside>
      </div>
    </div>
  );
}
