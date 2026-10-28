import type { Mode } from "./api";

// What each answering mode does, in the words the interface shows.
export const MODE_HELP: Record<Mode, string> = {
  agent: "Agent: can search again, read more pages, or ask you to clarify.",
  baseline: "Single pass: searches once, then answers from those results. Useful for comparing approaches.",
};
