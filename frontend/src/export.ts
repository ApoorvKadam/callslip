import type { Run } from "./api";
import { copied } from "./components/AnswerView";

const VERDICT: Record<string, string> = {
  supported: "supports its sentence",
  partly: "partly supports its sentence",
  not_supported: "does not support its sentence",
};

// One answer as Markdown, from its checked record: the question, the answer with its citation
// numbers, then each source with its page, quote and the results of the two checks. Nothing is
// generated again; it is the answer as shown.
export function answerMarkdown(run: Run, origin: string): string {
  const answer = run.answer;
  if (!answer) return "";
  const when = new Date(run.finished_at ?? run.created_at).toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
  const mode = run.mode === "agent" ? "Agent" : "Single pass";
  // Text copied word for word from a source gets quotation marks, as on screen.
  const byNumber = new Map(answer.citations.map((c) => [c.number, c]));
  let body = "";
  answer.segments.forEach((seg, i) => {
    let text = seg.text;
    if (seg.citations.length > 0) {
      const [, lead, core, trail] = /^(\s*)([\s\S]*?)(\s*)$/.exec(text) ?? ["", "", text, ""];
      const sources = seg.citations.flatMap((n) => byNumber.get(n) ?? []);
      const after = answer.segments[i + 1]?.text ?? "";
      if (copied(core, body, after, sources)) text = `${lead}“${core}”${trail}`;
      text = text.replace(/\s*$/, (end) => seg.citations.map((n) => ` [${n}]`).join("") + end);
    }
    body += text;
  });
  body = body.trim();
  const lines = [`# ${run.question}`, "", `Callslip, ${mode}, ${when}.`, "", body, ""];
  if (answer.citations.length > 0) {
    lines.push("## Sources", "");
    for (const c of answer.citations) {
      const verdict = answer.support?.find((s) => s.citations.includes(c.number))?.verdict;
      const checks = [
        c.provenance === "verified" ? `quote found on page ${c.page_no}` : "quote not found on the page",
        verdict && VERDICT[verdict],
      ].filter(Boolean);
      // The citation's title already ends with its page.
      const title = c.title.replace(/, page \d+$/, "");
      const page = c.page_no ? `, page ${c.page_no}` : "";
      const link =
        c.document_id && c.page_no
          ? ` ([open](${origin}/api/documents/${c.document_id}/file#page=${c.page_no}))`
          : "";
      lines.push(`${c.number}. ${title}${page}${link}: ${checks.join("; ")}.`);
      const quote = c.cited_text.split(/\s+/).join(" ").trim();
      if (quote) lines.push(`   > ${quote}`);
    }
    lines.push(
      "",
      "Links to a document uploaded privately open only for the account that uploaded it.",
    );
  }
  return lines.join("\n") + "\n";
}

// Save text as a file through the browser.
export function download(name: string, text: string): void {
  const url = URL.createObjectURL(new Blob([text], { type: "text/markdown;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}
