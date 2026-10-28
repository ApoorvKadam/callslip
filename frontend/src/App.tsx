import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiError,
  type Mode,
  type Run,
  type Answer,
  type RunEvent,
  type SessionSummary,
  type SupportCheck,
  type RunStatus,
  abandon,
  ask,
  createSession,
  getAccount,
  getRun,
  getSession,
  listSessions,
  resume,
  runEventsUrl,
} from "./api";
import { AccountMenu } from "./components/AccountMenu";
import { Conversation, type LiveAnswer, type PendingClarification } from "./components/Conversation";
import { ConversationList } from "./components/ConversationList";
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
  "answer_delta",
  "answer",
  "support",
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

  // Each switch of conversation takes a ticket; a reply for an older ticket is ignored, so a
  // slow load can never replace the conversation chosen after it.
  const switches = useRef(0);

  const startSession = useCallback(async () => {
    const ticket = ++switches.current;
    const { id } = await createSession();
    if (ticket !== switches.current) return;
    localStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
    setRuns([]);
    setEvents({});
    setSelectedId(null);
  }, []);

  // Who is signed in, if anyone: it decides which documents are visible and searched.
  const [account, setAccount] = useState<string | null>(null);
  useEffect(() => {
    getAccount()
      .then((a) => setAccount(a.email))
      .catch(() => setAccount(null));
  }, []);

  // Show a conversation: its questions, with the last one selected and followed if running.
  const openSession = useCallback(
    async (id: string) => {
      const ticket = ++switches.current;
      const session = await getSession(id);
      if (ticket !== switches.current) return;
      localStorage.setItem(SESSION_KEY, session.id);
      setSessionId(session.id);
      setRuns(session.runs);
      setEvents({});
      setSelectedId(null);
      const last = session.runs.at(-1);
      if (last) {
        setSelectedId(last.id);
        if (last.status === "running") follow(last.id);
        else await refreshRun(last.id);
      }
    },
    [follow, refreshRun],
  );

  // Earlier conversations, kept current as questions are asked and accounts change.
  const [history, setHistory] = useState<SessionSummary[]>([]);
  const [side, setSide] = useState<"documents" | "conversations">("documents");
  useEffect(() => {
    let current = true;
    listSessions()
      .then((list) => current && setHistory(list))
      .catch(() => current && setHistory([]));
    return () => {
      current = false;
    };
  }, [sessionId, runs.length, account]);

  // Restore the last session in this browser, or start a new one.
  useEffect(() => {
    const saved = localStorage.getItem(SESSION_KEY);
    (async () => {
      try {
        if (saved) {
          await openSession(saved);
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
  }, [openSession, startSession]);

  // What each question's events already show: its answer as soon as the answer event arrives,
  // or, while the model is still writing it, the text so far. A turn that ended in a tool call
  // was the model working, not answering, so its text is not shown.
  const live: Record<string, LiveAnswer> = {};
  for (const run of runs) {
    const list = events[run.id] ?? [];
    const answerEvent = list.find((e) => e.type === "answer");
    if (answerEvent) {
      const supportEvent = list.find((e) => e.type === "support");
      const answer = answerEvent.data as unknown as Answer;
      live[run.id] = {
        answer: supportEvent
          ? { ...answer, support: supportEvent.data.checks as SupportCheck[] }
          : answer,
      };
      continue;
    }
    if (run.answer || list.some((e) => e.type === "run_finished")) continue;
    const deltas = list.filter((e) => e.type === "answer_delta");
    if (deltas.length === 0) continue;
    const turn = Math.max(...deltas.map((e) => Number(e.data.turn)));
    const ended = list.some(
      (e) =>
        e.type === "model_call" && Number(e.data.turn) === turn && e.data.stop_reason === "tool_use",
    );
    if (ended) continue;
    const draft = deltas
      .filter((e) => Number(e.data.turn) === turn)
      .map((e) => String(e.data.text))
      .join("");
    live[run.id] = { draft };
  }

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

  // Runs as shown: a run's answer from its events until the stored run is read again.
  const shown: Run[] = runs.map((r) => {
    const early = live[r.id]?.answer;
    return !r.answer && early ? { ...r, answer: early } : r;
  });
  const selected = shown.find((r) => r.id === selectedId) ?? null;

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
          <AccountMenu
            email={account}
            onChange={(email) => {
              // A conversation belongs to the account that started it, so start a new one.
              setAccount(email);
              void startSession().catch((e) => setError(`Could not start a session: ${errorText(e)}`));
            }}
          />
        </div>
      </header>
      <div className="layout">
        <aside className="docs" aria-label="Documents and conversations">
          <div className="tabs side-tabs" role="tablist" aria-label="Library">
            <button
              type="button"
              role="tab"
              id="tab-documents"
              aria-controls="panel-documents"
              aria-selected={side === "documents"}
              className="tab"
              onClick={() => setSide("documents")}
            >
              Documents
            </button>
            <button
              type="button"
              role="tab"
              id="tab-conversations"
              aria-controls="panel-conversations"
              aria-selected={side === "conversations"}
              className="tab"
              onClick={() => setSide("conversations")}
            >
              Conversations <span className="meta">{history.length || ""}</span>
            </button>
          </div>
          {side === "documents" ? (
            <div role="tabpanel" id="panel-documents" aria-labelledby="tab-documents">
              <DocumentsPanel signedIn={account !== null} />
            </div>
          ) : (
            <div role="tabpanel" id="panel-conversations" aria-labelledby="tab-conversations">
              <ConversationList
                items={history}
                currentId={sessionId}
                onOpen={(id) =>
                  void openSession(id).catch((e) =>
                    setError(`Could not open that conversation: ${errorText(e)}`),
                  )
                }
              />
            </div>
          )}
        </aside>
        <main className="talk">
          <Conversation
            runs={shown}
            live={live}
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
