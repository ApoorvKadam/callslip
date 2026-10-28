import { useCallback, useEffect, useRef, useState } from "react";
import {
  type Run,
  type RunEvent,
  ask,
  createSession,
  getRun,
  getSession,
  runEventsUrl,
} from "./api";
import { Conversation } from "./components/Conversation";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { TracePanel } from "./components/TracePanel";

const SESSION_KEY = "agentic-rag.session";
const EVENT_TYPES = ["run_started", "tool_call", "model_call", "answer", "run_finished"];

function errorText(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [events, setEvents] = useState<Record<string, RunEvent[]>>({});
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
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
      source.addEventListener("end", () => {
        source.close();
        delete streams.current[id];
        void refreshRun(id);
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
      } catch {
        // Unknown or expired session: start fresh.
      }
      try {
        await startSession();
      } catch (e) {
        setError(`Could not start a session: ${errorText(e)}`);
      }
    })();
  }, [follow, refreshRun, startSession]);

  async function onAsk(question: string): Promise<boolean> {
    if (!sessionId) return false;
    setError(null);
    try {
      const run = await ask(sessionId, question, "baseline");
      setRuns((all) => [...all, run]);
      setSelectedId(run.id);
      follow(run.id);
      return true;
    } catch (e) {
      setError(errorText(e));
      return false;
    }
  }

  async function onSelect(id: string) {
    setSelectedId(id);
    if (!events[id]) await refreshRun(id);
  }

  const selected = runs.find((r) => r.id === selectedId) ?? null;

  return (
    <div className="app">
      <header className="topbar">
        <h1>Agentic RAG</h1>
        <p className="muted">Ask questions across your PDFs. Every answer cites document and page.</p>
      </header>
      <div className="layout">
        <aside className="sidebar">
          <DocumentsPanel />
        </aside>
        <main className="main">
          <Conversation
            runs={runs}
            selectedId={selectedId}
            onSelect={(id) => void onSelect(id)}
            onAsk={onAsk}
            onNewSession={() => void startSession()}
            error={error}
          />
        </main>
        <aside className="trace">
          <TracePanel run={selected} events={selected ? (events[selected.id] ?? []) : []} />
        </aside>
      </div>
    </div>
  );
}
