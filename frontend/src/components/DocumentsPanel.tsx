import { useCallback, useEffect, useRef, useState } from "react";
import {
  type DocumentInfo,
  type DocumentStatus,
  documentFileUrl,
  listDocuments,
  uploadDocument,
} from "../api";
import { shortCode, titleRest } from "../format";

const STATUS_MARK: Record<DocumentStatus, string> = {
  queued: "mark",
  processing: "mark mark-wait",
  ready: "mark mark-ok",
  failed: "mark mark-bad",
};

const STATUS_LABEL: Record<DocumentStatus, string> = {
  queued: "Queued",
  processing: "Processing",
  ready: "Ready",
  failed: "Failed",
};

function errorText(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

export function DocumentsPanel() {
  const [docs, setDocs] = useState<DocumentInfo[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const [uploading, setUploading] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  const refresh = useCallback(async () => {
    try {
      setDocs(await listDocuments());
      setLoadError(null);
    } catch (e) {
      setLoadError(`Could not load documents: ${errorText(e)}`);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Poll only while something is still being processed.
  const pending = docs.some((d) => d.status === "queued" || d.status === "processing");
  useEffect(() => {
    if (!pending) return;
    const timer = setInterval(() => void refresh(), 2000);
    return () => clearInterval(timer);
  }, [pending, refresh]);

  async function upload(files: FileList | null) {
    if (!files || files.length === 0) return;
    setUploading(true);
    const results: string[] = [];
    for (const file of Array.from(files)) {
      try {
        await uploadDocument(file);
        results.push(`${file.name}: uploaded`);
      } catch (e) {
        results.push(`${file.name}: ${errorText(e)}`);
      }
    }
    setNotice(results.join(". "));
    setUploading(false);
    if (input.current) input.current.value = "";
    await refresh();
  }

  const ready = docs.filter((d) => d.status === "ready").length;

  return (
    <section aria-labelledby="documents-heading">
      <div className="docs-head">
        <h2 id="documents-heading" className="label">
          Documents
        </h2>
        <span className="meta">
          {ready === docs.length ? `${ready} ready` : `${ready} of ${docs.length} ready`}
        </span>
      </div>

      <label className={`btn upload${uploading ? " busy" : ""}`}>
        <input
          ref={input}
          type="file"
          accept="application/pdf,.pdf"
          multiple
          disabled={uploading}
          onChange={(e) => void upload(e.target.files)}
        />
        <span>{uploading ? "Uploading" : "Upload PDFs"}</span>
      </label>
      <p className="notice meta" role="status" aria-live="polite">
        {notice}
      </p>
      {loadError && (
        <p className="error" role="alert">
          {loadError}
        </p>
      )}

      {docs.length === 0 && !loadError && (
        <p className="meta">No documents yet. Upload text-based PDFs to start.</p>
      )}
      <ul className="doc-list">
        {docs.map((d) => (
          <li key={d.id} className="doc">
            <a
              href={documentFileUrl(d.id)}
              target="_blank"
              rel="noreferrer"
              title={d.title}
              aria-label={`${d.title}, opens the PDF`}
            >
              <span className="doc-code">
                {shortCode(d.title)}
                {d.status !== "ready" && (
                  <span className={STATUS_MARK[d.status]}>{STATUS_LABEL[d.status]}</span>
                )}
              </span>
              <span className="doc-title">{titleRest(d.title)}</span>
              <span className="meta">
                {d.page_count ? `${d.page_count} pages` : d.filename}
                {d.chunk_count ? `, ${d.chunk_count} passages` : ""}
              </span>
            </a>
            {d.error && <p className="error meta">{d.error}</p>}
          </li>
        ))}
      </ul>
    </section>
  );
}
