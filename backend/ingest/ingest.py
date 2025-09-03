# ingest/ingest.py
import asyncio, uuid, json, os
from pathlib import Path
from typing import List
from pgvector import Vector                      # ← NEU
from app.db import get_conn                      # ← statt direkte psycopg.connect
from .loaders import load_documents
from .chunker import split_into_chunks, to_records
from app.embeddings import WatsonxAIEmbeddings
MAX_TOKENS = 500

def approx_tokens(s: str) -> int:
    return max(1, int(len(s)/4))

def hard_trim_to_tokens(s: str, max_tokens: int) -> str:
    max_chars = max_tokens * 4
    return s[:max_chars]
async def embed_and_upsert(records: List[dict]):
    if not records:
        return
    provider = WatsonxAIEmbeddings()

    texts = []
    for r in records:
        txt = r["content"]
        if approx_tokens(txt) > MAX_TOKENS:
            txt = hard_trim_to_tokens(txt, MAX_TOKENS - 10)
        texts.append(txt)

    vectors = await provider.embed(texts)

    with get_conn() as conn, conn.cursor() as cur:   # ← nutzt register_vector()
        for rec, emb in zip(records, vectors):
            cur.execute(
                """
                INSERT INTO documents (id, doc_id, chunk_id, content, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  content=EXCLUDED.content,
                  metadata=EXCLUDED.metadata,
                  embedding=EXCLUDED.embedding
                """,
                (
                    str(uuid.uuid4()),
                    rec["doc_id"],
                    rec["chunk_id"],
                    rec["content"],
                    json.dumps(rec["metadata"]),
                    Vector(emb),                  # ← WICHTIG: als pgvector.Vector
                ),
            )

async def main(input_dir: str):
    print("CWD:", Path.cwd())
    print("Input dir:", input_dir)
    print("Resolved root:", Path(input_dir).resolve())
    print("Files found:", len(list(Path(input_dir).resolve().rglob('*.*'))))

    root = Path(input_dir).resolve()
    paths = list(root.rglob("*.*"))
    docs = list(load_documents(paths))
    print(f"CWD: {Path.cwd()}")
    print(f"Scanning: {root}")
    print(f"Loaded {len(docs)} docs")

    batch: List[dict] = []
    for d in docs:
        chunks = split_into_chunks(d["text"])
        batch.extend(to_records(d["doc_id"], chunks, d["metadata"]))

    print(f"Prepared {len(batch)} chunks")
    if not batch:                                  # ← NEU: Guard
        print("No chunks to ingest. Abort.")
        return

    # optional batching hier – bei wenigen Chunks nicht nötig
    await embed_and_upsert(batch)
    print("Ingestion complete.")


# ingest/ingest.py (ganz unten ergänzen)
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m ingest.ingest <input_dir>")
        raise SystemExit(2)
    asyncio.run(main(sys.argv[1]))
