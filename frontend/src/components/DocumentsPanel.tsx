import { Trash2, Upload } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  type DocumentInfo,
  type DocumentStatus,
  deleteDocument,
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

export function DocumentsPanel({ signedIn }: { signedIn: boolean }) {
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

  // Signing in or out changes which documents are visible.
  useEffect(() => {
    void refresh();
  }, [refresh, signedIn]);

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

  // Deleting is final, so it asks first; the list then shows what is left.
  async function remove(doc: DocumentInfo) {
    if (!window.confirm(`Delete "${doc.title}"? It is removed for good, with its passages.`)) return;
    try {
      await deleteDocument(doc.id);
      setNotice(`${doc.title}: deleted`);
    } catch (e) {
      setNotice(`${doc.title}: ${errorText(e)}`);
    }
    await refresh();
  }

  const ready = docs.filter((d) => d.status === "ready").length;
  const mine = docs.filter((d) => d.private);
  const shared = docs.filter((d) => !d.private);

  return (
    <section aria-labelledby="documents-heading">
      <div className="docs-head">
        <h2 id="documents-heading" className="visually-hidden">
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
        <span>
          <Upload size={15} aria-hidden="true" />
          {uploading ? "Uploading" : signedIn ? "Upload privately" : "Upload to shared collection"}
        </span>
      </label>
      {!signedIn && (
        <p className="meta">
          Without signing in, uploaded PDFs are visible to everyone using this deployment. Sign in
          to upload privately.
        </p>
      )}
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
      {signedIn && (
        <>
          <h3 className="label doc-group">Your documents</h3>
          {mine.length === 0 && <p className="meta">Only you can see what you upload here.</p>}
          <DocList docs={mine} onDelete={(d) => void remove(d)} />
          <h3 className="label doc-group">Shared collection</h3>
        </>
      )}
      <DocList docs={shared} />
    </section>
  );
}

function DocList({
  docs,
  onDelete,
}: {
  docs: DocumentInfo[];
  onDelete?: (doc: DocumentInfo) => void;
}) {
  return (
    <ul className="doc-list">
      {docs.map((d) => (
        <li key={d.id} className={onDelete ? "doc doc-own" : "doc"}>
          <a
            href={documentFileUrl(d.id)}
            target="_blank"
            rel="noreferrer"
            title={d.title}
            aria-label={`${d.title}${d.status === "ready" ? "" : `, ${STATUS_LABEL[d.status]}`}, opens the PDF`}
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
          {onDelete && d.status !== "queued" && d.status !== "processing" && (
            <button
              type="button"
              className="icon-button"
              aria-label={`Delete ${d.title}`}
              title="Delete"
              onClick={() => onDelete(d)}
            >
              <Trash2 size={15} aria-hidden="true" />
            </button>
          )}
          {d.error && <p className="error meta">{d.error}</p>}
        </li>
      ))}
    </ul>
  );
}
