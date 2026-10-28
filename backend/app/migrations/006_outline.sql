-- A document's own bookmarks (title, physical page, level), read at ingestion. NULL until read;
-- an empty array when the PDF has none. The worker fills NULLs for documents ingested earlier.
ALTER TABLE documents ADD COLUMN outline JSONB;
