import { DocumentsPanel } from "./components/DocumentsPanel";

export default function App() {
  return (
    <div className="app">
      <header className="topbar">
        <h1>Agentic RAG</h1>
        <p className="muted">Ask questions across your PDFs. Every answer cites document and page.</p>
      </header>
      <div className="layout">
        <aside className="sidebar">
          <DocumentsPanel />
        </aside>
        <main className="main">
          <section className="panel empty">
            <h2>Questions</h2>
            <p className="muted">
              Upload PDFs on the left. Asking questions is added in the next change.
            </p>
          </section>
        </main>
      </div>
    </div>
  );
}
