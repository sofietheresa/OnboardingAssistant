import asyncio, uuid, json, os
from pathlib import Path
from typing import List
import psycopg
from psycopg.rows import dict_row

from loaders import load_documents
from chunker import split_into_chunks, to_records
from app.embeddings import WatsonxAIEmbeddings

DB_URL = os.environ["DATABASE_URL"]

async def embed_and_upsert(records: List[dict]):
    """
    Embeddings erzeugen (watsonx.ai) und in Postgres upserten.
    """
    provider = WatsonxAIEmbeddings()
    texts = [r["content"] for r in records]
    vectors = await provider.embed(texts)

    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
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
                        emb,
                    ),
                )
        conn.commit()

async def main(input_dir: str):
    paths = list(Path(input_dir).rglob("*.*"))
    docs = list(load_documents(paths))
    print(f"Loaded {len(docs)} docs")

    batch: List[dict] = []
    for d in docs:
        chunks = split_into_chunks(d["text"])
        recs = to_records(d["doc_id"], chunks, d["metadata"])
        batch.extend(recs)

    print(f"Prepared {len(batch)} chunks")
    await embed_and_upsert(batch)
    print("Ingestion complete.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m ingest.ingest <input_dir>")
        raise SystemExit(1)
    asyncio.run(main(sys.argv[1]))
