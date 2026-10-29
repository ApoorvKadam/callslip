import { Check, ChevronDown, ChevronRight, X } from "lucide-react";
import { useEffect, useState } from "react";
import { dollars, seconds } from "../format";

// The committed evaluation runs, from evaluation.json (written by scripts/eval_digest.py).
interface Repeat {
  repeat: number;
  passed: boolean;
  status: string;
  notes: string[];
  tool_calls: number;
  answer_ms: number | null;
  cost_usd: number;
  cited_pages: string[];
  answer: string;
}

interface Case {
  id: string;
  category: string;
  question: string;
  expect: string;
  required: string[];
  gold: { doc: string; pages: number[] }[];
  systems: Record<string, Repeat[]>;
}

interface Totals {
  passed: number;
  completed: number;
  runs: number;
  citations: number;
  citations_verified: number;
  median_answer_ms: number | null;
  mean_tool_calls: number;
  cost_usd: number;
}

interface EvalRun {
  run: string;
  label: string;
  systems: Record<string, Totals>;
  cases: Case[];
}

const NAME: Record<string, string> = { agent: "Agent", baseline: "Single pass" };

export function EvaluationView() {
  const [runs, setRuns] = useState<EvalRun[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [which, setWhich] = useState(0);
  const [open, setOpen] = useState<string | null>(null);

  useEffect(() => {
    fetch("/evaluation.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`${r.status} ${r.statusText}`))))
      .then(setRuns)
      .catch((e: Error) => setError(`Could not load the evaluation: ${e.message}`));
  }, []);

  if (error) {
    return (
      <p className="error" role="alert">
        {error}
      </p>
    );
  }
  if (!runs) return <p className="meta">Loading</p>;
  const run = runs[which];
  const systems = Object.keys(run.systems);

  return (
    <div className="evaluation-view">
      <h1>Evaluation</h1>
      <p className="meta">
        Fifteen cases, three repeats each, graded by fixed checks: required facts, citations found
        on their pages, the right pages cited, and the behaviour each case expects. The single pass
        searches once, on the same documents and model.
      </p>
      <div className="segmented eval-runs" role="group" aria-label="Evaluation run">
        {runs.map((r, i) => (
          <button
            key={r.run}
            type="button"
            className={i === which ? "on" : undefined}
            aria-pressed={i === which}
            onClick={() => {
              setWhich(i);
              setOpen(null);
            }}
          >
            {r.label}
          </button>
        ))}
      </div>

      <table className="eval-table">
        <caption className="visually-hidden">Totals for run {run.run}</caption>
        <thead>
          <tr>
            <th scope="col">System</th>
            <th scope="col">Runs passing every check</th>
            <th scope="col">Completed</th>
            <th scope="col">Citations found on their page</th>
            <th scope="col">Time to answer, median</th>
            <th scope="col">Tool calls, mean</th>
            <th scope="col">Cost</th>
          </tr>
        </thead>
        <tbody>
          {systems.map((s) => {
            const t = run.systems[s];
            return (
              <tr key={s}>
                <th scope="row">{NAME[s] ?? s}</th>
                <td>
                  {t.passed} of {t.runs}
                </td>
                <td>
                  {t.completed} of {t.runs}
                </td>
                <td>
                  {t.citations_verified} of {t.citations}
                </td>
                <td>{t.median_answer_ms ? seconds(t.median_answer_ms) : "-"}</td>
                <td>{t.mean_tool_calls}</td>
                <td>{dollars(t.cost_usd)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <table className="eval-table eval-cases">
        <caption className="visually-hidden">Cases of run {run.run}</caption>
        <thead>
          <tr>
            <th scope="col">Case</th>
            {systems.map((s) => (
              <th key={s} scope="col">
                {NAME[s] ?? s}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {run.cases.map((c) => (
            <CaseRow
              key={c.id}
              c={c}
              systems={systems}
              open={open === c.id}
              onToggle={() => setOpen(open === c.id ? null : c.id)}
            />
          ))}
        </tbody>
      </table>
      <p className="meta">
        Every run, with its traces, is in <code>eval/results/{run.run}</code> in the repository.
      </p>
    </div>
  );
}

function CaseRow(props: { c: Case; systems: string[]; open: boolean; onToggle: () => void }) {
  const { c, systems, open, onToggle } = props;
  const Chevron = open ? ChevronDown : ChevronRight;
  return (
    <>
      <tr>
        <th scope="row">
          <button
            type="button"
            className="eval-case"
            aria-expanded={open}
            aria-controls={`case-${c.id}`}
            onClick={onToggle}
          >
            <Chevron size={14} aria-hidden="true" />
            {c.id.replace(/-/g, " ")}
          </button>
        </th>
        {systems.map((s) => (
          <td key={s}>
            <Marks repeats={c.systems[s] ?? []} />
          </td>
        ))}
      </tr>
      {open && (
        <tr id={`case-${c.id}`}>
          <td colSpan={systems.length + 1} className="eval-detail">
            <p>
              <strong>Question.</strong> {c.question}
            </p>
            <p className="meta">
              Expected: {c.category} ({c.expect}); required{" "}
              {c.required.length ? c.required.map((r) => `"${r}"`).join(", ") : "nothing more"};
              gold pages {c.gold.map((g) => `${g.doc} p. ${g.pages.join(", ")}`).join("; ")}.
            </p>
            <div className="eval-answers">
              {systems.map((s) => (
                <SystemAnswers key={s} name={NAME[s] ?? s} repeats={c.systems[s] ?? []} />
              ))}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

// One mark per repeat: a tick for a run that passed every check, a cross for one that did not.
function Marks({ repeats }: { repeats: Repeat[] }) {
  const passed = repeats.filter((r) => r.passed).length;
  return (
    <span className="eval-marks" aria-label={`${passed} of ${repeats.length} passed`}>
      {repeats.map((r) =>
        r.passed ? (
          <Check key={r.repeat} size={15} className="pass" aria-hidden="true" />
        ) : (
          <X key={r.repeat} size={15} className="fail" aria-hidden="true" />
        ),
      )}
      <span className="meta">
        {passed} of {repeats.length}
      </span>
    </span>
  );
}

function SystemAnswers({ name, repeats }: { name: string; repeats: Repeat[] }) {
  const first = repeats[0];
  if (!first) return null;
  const failures = repeats.filter((r) => !r.passed);
  return (
    <section>
      <h3>{name}</h3>
      <p className="meta">
        Repeat 1: {first.passed ? "passed" : "failed"}, {first.status}, {first.tool_calls} tool
        calls{first.answer_ms ? `, ${seconds(first.answer_ms)} to answer` : ""},{" "}
        {dollars(first.cost_usd)}. Cited {first.cited_pages.join(", ") || "nothing"}.
      </p>
      <blockquote>{first.answer || "No answer."}</blockquote>
      {failures.map((r) => (
        <p key={r.repeat} className="meta check-warn">
          Repeat {r.repeat} failed: {r.notes.join("; ") || r.status}.
        </p>
      ))}
    </section>
  );
}
