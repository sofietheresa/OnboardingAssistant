from typing import List, Dict
from pgvector import Vector
from .embeddings import WatsonxAIEmbeddings
from .llm import WatsonxAILLM
from .db import get_conn

SYSTEM_PROMPT = (
    "Du bist ein Onboarding-Assistent der Firma. Antworte kurz, korrekt, auf Deutsch. "
    "Nutze ausschließlich die bereitgestellten Kontexte. Wenn du unsicher bist, "
    "sage dies klar und schlage einen Eskalationsweg vor. Nenne immer die Quellen (Titel#Chunk)."
)

def format_prompt(question: str, contexts: List[Dict]) -> str:
    """
    Baut einen klaren Prompt mit den Top-K Kontext-Chunks.
    """
    lines = []
    for c in contexts:
        title = c["metadata"].get("filename") or c["doc_id"]
        lines.append(f"[{title}#{c['chunk_id']}] {c['content']}")
    ctx = "\n\n".join(lines[:8])  # maximal 8 Chunks

    return (
        f"FRAGE:\n{question}\n\n"
        f"KONTEXT (verwende NUR Folgendes):\n{ctx}\n\n"
        "ANTWORTFORMAT:\n"
        "- knappe Antwort in Deutsch\n"
        "- bei Prozessen: nummerierte Schritte\n"
        "- Abschlusszeile: 'Quellen: <Titel#Chunk, ...>'\n"
    )

async def retrieve(query: str, k: int = 6) -> List[Dict]:
    embedder = WatsonxAIEmbeddings()
    q_raw = (await embedder.embed([query]))[0]  # -> List[float]
    q_vec = Vector(q_raw)                       # ← WICHTIG: in pgvector.Vector wandeln

    sql = """
    SELECT id, doc_id, chunk_id, content, metadata
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (q_vec, k))
            rows = cur.fetchall()
            return rows

async def answer(question: str) -> Dict:
    contexts = await retrieve(question, k=6)
    prompt = format_prompt(question, contexts)

    llm = WatsonxAILLM()
    output = await llm.generate(SYSTEM_PROMPT, prompt)

    sources = [
        {
            "title": c["metadata"].get("filename") or c["doc_id"],
            "doc_id": c["doc_id"],
            "chunk_id": c["chunk_id"],
        }
        for c in contexts
    ]
    return {"answer": output, "sources": sources}
