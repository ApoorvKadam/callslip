import { ExternalLink, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { documentFileUrl } from "../api";
import { shortCode } from "../format";

// One cited page, drawn from the PDF itself, with the quote marked on it. PDF.js loads only when
// a page is first opened, so it adds nothing to the first page load.

export interface PreviewTarget {
  documentId: number;
  title: string;
  page: number;
  quote: string;
}

type Found = "pending" | "marked" | "not-found" | "repeated";

// Where the quote sits among the page's text pieces. Only letters and digits are compared, so
// line breaks, hyphenation and spacing that differ between PDF readers do not matter. A quote
// that cannot be placed, or appears more than once, is not marked at all rather than guessed.
export function locateQuote(
  pieces: string[],
  quote: string,
): { first: number; last: number } | "not-found" | "repeated" {
  const letters: string[] = [];
  const owner: number[] = [];
  pieces.forEach((piece, i) => {
    for (const ch of piece.normalize("NFKC").toLowerCase()) {
      if (/[\p{L}\p{N}]/u.test(ch)) {
        letters.push(ch);
        owner.push(i);
      }
    }
  });
  const page = letters.join("");
  const wanted = [...quote.normalize("NFKC").toLowerCase()]
    .filter((ch) => /[\p{L}\p{N}]/u.test(ch))
    .join("");
  if (wanted.length < 8) return "not-found";
  const at = page.indexOf(wanted);
  if (at < 0) return "not-found";
  if (page.indexOf(wanted, at + 1) >= 0) return "repeated";
  return { first: owner[at], last: owner[at + wanted.length - 1] };
}

export function PagePreview({ target, onClose }: { target: PreviewTarget; onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const textLayer = useRef<HTMLDivElement>(null);
  const sheet = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<"loading" | "ready" | "failed">("loading");
  const [found, setFound] = useState<Found>("pending");

  // A modal dialog: focus moves into it, Escape closes it, and focus returns to the button.
  // Unmounting removes it, which ends the modal state; closing it here would report a close.
  useEffect(() => {
    if (dialog.current && !dialog.current.open) dialog.current.showModal();
  }, []);

  useEffect(() => {
    let stopped = false;
    let cleanup = () => {};
    setState("loading");
    setFound("pending");
    (async () => {
      const pdfjs = await import("pdfjs-dist");
      const worker = await import("pdfjs-dist/build/pdf.worker.min.mjs?url");
      pdfjs.GlobalWorkerOptions.workerSrc = worker.default;
      if (stopped) return; // closed while PDF.js was loading
      // Same-origin, with the session cookie, so private documents open only for their owner.
      const task = pdfjs.getDocument({
        url: documentFileUrl(target.documentId),
        enableXfa: false,
      });
      cleanup = () => void task.destroy();
      const doc = await task.promise;
      const page = await doc.getPage(target.page);
      if (stopped || !canvas.current || !textLayer.current || !sheet.current) return;
      // The content width: the sheet's padding and the page's 1 px border do not hold the page.
      const style = getComputedStyle(sheet.current);
      const inner =
        sheet.current.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
      const width = Math.min(inner - 2 || 820, 900);
      const viewport = page.getViewport({ scale: width / page.getViewport({ scale: 1 }).width });
      const ratio = window.devicePixelRatio || 1;
      const c = canvas.current;
      c.width = Math.floor(viewport.width * ratio);
      c.height = Math.floor(viewport.height * ratio);
      c.style.width = `${Math.floor(viewport.width)}px`;
      c.style.height = `${Math.floor(viewport.height)}px`;
      sheet.current.style.setProperty("--total-scale-factor", String(viewport.scale));
      await page.render({
        canvas: c,
        viewport,
        transform: ratio === 1 ? undefined : [ratio, 0, 0, ratio, 0, 0],
      }).promise;
      textLayer.current.replaceChildren();
      const layer = new pdfjs.TextLayer({
        textContentSource: await page.getTextContent(),
        container: textLayer.current,
        viewport,
      });
      await layer.render();
      if (stopped) return;
      const spot = locateQuote(layer.textContentItemsStr, target.quote);
      if (typeof spot === "string") {
        setFound(spot);
      } else {
        for (let i = spot.first; i <= spot.last; i += 1) layer.textDivs[i]?.classList.add("hit");
        setFound("marked");
        layer.textDivs[spot.first]?.scrollIntoView({ block: "center" });
      }
      setState("ready");
    })().catch(() => {
      if (!stopped) setState("failed");
    });
    return () => {
      stopped = true;
      cleanup();
    };
  }, [target]);

  return (
    <dialog
      ref={dialog}
      className="page-preview"
      aria-labelledby="preview-title"
      onClose={onClose}
      onClick={(e) => {
        // A click on the backdrop closes it, as with any dialog. The backdrop and the dialog's own
        // margins report the same target, so only a click outside its box counts.
        const box = dialog.current?.getBoundingClientRect();
        const outside =
          box &&
          (e.clientX < box.left ||
            e.clientX > box.right ||
            e.clientY < box.top ||
            e.clientY > box.bottom);
        if (e.target === dialog.current && outside) dialog.current?.close();
      }}
    >
      <header className="preview-head">
        <h2 id="preview-title">
          {shortCode(target.title)} <span className="meta">page {target.page}</span>
        </h2>
        <a
          className="text-button"
          href={documentFileUrl(target.documentId, target.page)}
          target="_blank"
          rel="noreferrer"
        >
          <ExternalLink size={14} aria-hidden="true" />
          Open the PDF
        </a>
        <button
          type="button"
          className="icon-button"
          aria-label="Close"
          onClick={() => dialog.current?.close()}
        >
          <X size={16} aria-hidden="true" />
        </button>
      </header>
      <p className="preview-quote">
        <span className="label">Quoted</span> {target.quote}
      </p>
      <p className="meta preview-status" role="status">
        {state === "loading" && "Drawing the page"}
        {state === "failed" && "Could not draw this page. Open the PDF instead."}
        {state === "ready" && found === "marked" && "The quote is marked on the page."}
        {state === "ready" &&
          found === "not-found" &&
          "The quote was checked on this page, but it could not be marked on the drawing."}
        {state === "ready" &&
          found === "repeated" &&
          "The quote appears more than once on this page, so it is not marked."}
      </p>
      <div className="preview-body" ref={sheet}>
        <div className="preview-page">
          <canvas ref={canvas} aria-hidden="true" />
          <div className="textLayer" ref={textLayer} />
        </div>
      </div>
    </dialog>
  );
}
