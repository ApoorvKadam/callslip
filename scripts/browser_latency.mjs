// What a user waits for, measured in a real browser: press Ask, then the first answer text on
// screen, the checked answer shown, and the quote check done. One new conversation per question.
//
//   npm i -D @playwright/test && npx playwright install chromium
//   BASE=http://localhost:8080 REPEATS=3 node scripts/browser_latency.mjs
import { chromium } from '@playwright/test';
const BASE = process.env.BASE ?? 'http://localhost:8080';
const QUESTIONS = [
  'What are the four functions of the NIST AI RMF Core?',
  "What change to the NIST AI RMF does America's AI Action Plan recommend, and which characteristics of trustworthy AI does the AI RMF itself list?",
  'What fine does OMB M-25-21 set for an agency that misses its AI strategy deadline?',
  'How long do CFO Act agencies have to publish an AI strategy under the OMB AI memos?',
  'What does the Northbridge University AI Vendor Security Review Checklist require from vendors?',
];
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.goto(BASE); await p.locator('.composer textarea').waitFor();
const REPEATS = Number(process.env.REPEATS ?? 3);
const rows = [];
for (const q of QUESTIONS.flatMap((x) => Array(REPEATS).fill(x))) {
  await p.locator('header button:has-text("New conversation")').click(); await p.waitForTimeout(800);
  await p.locator('.composer textarea').fill(q);
  const t0 = Date.now();
  await p.locator('.composer textarea').press('Enter');
  let first = null, answered = null, done = null, shown = null;
  while (Date.now() - t0 < 120000) {
    const s = await p.evaluate(() => {
      const ex = [...document.querySelectorAll('article')].at(-1);
      const ans = ex?.querySelector('.answer');
      const meta = ex?.querySelector('.exchange-meta')?.textContent ?? '';
      const btn = document.querySelector('.composer button[type=submit]')?.textContent;
      return { text: (ans?.textContent ?? '').trim().length, streaming: !!ex?.querySelector('.answer.streaming'), meta, btn };
    });
    const t = Date.now() - t0;
    if (answered === null) {
      if (s.text > 0 && first === null) first = t;
      if (s.text === 0) first = null; // text of a turn that ended in a tool call disappears
    }
    if (answered === null && /Answered in/.test(s.meta)) { answered = t; shown = (s.meta.match(/Answered in ([\d.]+) s/) || [])[1]; }
    if (answered !== null && s.btn !== 'Working') { done = t; break; }
    await p.waitForTimeout(50);
  }
  rows.push({ q: q.slice(0, 48), first, answered, done, shown });
}
const fmt = (v) => (v == null ? '-' : `${(v / 1000).toFixed(1)} s`);
console.log('| Question | First answer text on screen | Answer shown | Check done | Server "Answered in" |');
console.log('|---|---|---|---|---|');
for (const r of rows) console.log(`| ${r.q} | ${fmt(r.first)} | ${fmt(r.answered)} | ${fmt(r.done)} | ${r.shown} s |`);
const stat = (k) => {
  const v = rows.map((r) => r[k]).filter((x) => x != null).sort((a, b) => a - b);
  const at = (q) => v[Math.min(v.length - 1, Math.round(q * (v.length - 1)))];
  return `median ${fmt(at(0.5))}, 90th percentile ${fmt(at(0.9))}, n=${v.length}`;
};
console.log(`\nFirst answer text: ${stat('first')}\nAnswer shown: ${stat('answered')}\nCheck done: ${stat('done')}`);
await b.close();
