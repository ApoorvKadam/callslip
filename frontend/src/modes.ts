import type { Mode } from "./api";

// How a question is asked: one way, or both at once to compare them.
export type AskMode = Mode | "compare";

// What each answering mode does, in the words the interface shows.
export const MODE_HELP: Record<AskMode, string> = {
  agent: "Agent: can search again, read more pages, or ask you to clarify.",
  baseline: "Single pass: searches once, then answers from those results. Useful for comparing approaches.",
  compare: "Compare: asks both ways at once and shows the two answers side by side.",
};
