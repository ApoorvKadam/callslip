// Small display helpers shared by the panels.

// "OMB M-25-21: Accelerating Federal Use of AI ..." -> "OMB M-25-21". Titles without a code
// before a colon use the part before the first comma, then their first words.
export function shortCode(title: string): string {
  const colon = title.indexOf(":");
  if (colon > 0 && colon <= 40) return title.slice(0, colon);
  const comma = title.indexOf(",");
  if (comma > 0 && comma <= 40) return title.slice(0, comma);
  return title.length > 40 ? `${title.slice(0, 38).trimEnd()}…` : title;
}

// The title without its short code: "Accelerating Federal Use of AI ...".
export function titleRest(title: string): string {
  const code = shortCode(title);
  for (const sep of [":", ","]) {
    if (title.startsWith(`${code}${sep}`)) return title.slice(code.length + 1).trim();
  }
  return title;
}

export function seconds(ms: number): string {
  return ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`;
}

export function count(n: number, one: string, many = `${one}s`): string {
  return `${n.toLocaleString("en-US")} ${n === 1 ? one : many}`;
}

// A short model turn can cost less than a hundredth of a cent, which would print as $0.0000.
export function dollars(value: number): string {
  if (value > 0 && value < 0.0001) return "under $0.0001";
  return `$${value.toFixed(4)}`;
}
