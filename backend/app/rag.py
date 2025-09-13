from typing import List, Dict
from .embeddings import WatsonxAIEmbeddings
from .llm import WatsonxAILLM
from .db import get_conn

SYSTEM_PROMPT = (
    "Du bist ein empathischer Onboarding-Assistent der Firma. Antworte kurz, korrekt, auf Deutsch. "
    "Nutze bevorzugt die bereitgestellten Kontexte, aber du darfst auch auf eigenes Wissen zurückgreifen, wenn du dir sicher bist. "
    "Wenn du unsicher bist, sage dies klar und schlage einen Eskalationsweg vor. "
    "Nenne die Quellen (Titel#Chunk) nur, wenn du dir sehr sicher bist, dass die Information aus dem Kontext stammt. "
    "Du darfst empathisch reagieren und Smalltalk führen, wenn es zur Situation passt."
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
    q_vec = (await embedder.embed([query]))[0]

    # als pgvector-kompatiblen String formatieren
    q_vec_str = "[" + ",".join(str(x) for x in q_vec) + "]"

    sql = """
    SELECT id, doc_id, chunk_id, content, metadata
    FROM documents
    ORDER BY embedding <=> %s::vector
    LIMIT %s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (q_vec_str, k))
            rows = cur.fetchall()
            return rows

async def answer(question: str) -> Dict:
    contexts = await retrieve(question, k=6)

    if contexts:  # normaler RAG-Flow
        prompt = format_prompt(question, contexts)
    else:  # kein Kontext gefunden → fallback
        prompt = (
            f"FRAGE:\n{question}\n\n"
            "Es konnte kein relevanter Kontext gefunden werden. "
            "Antworte bitte trotzdem kurz, korrekt, auf Deutsch, "
            "auf Basis deines eigenen Wissens. "
            "Wenn du unsicher bist, sage dies klar und schlage einen Eskalationsweg vor.\n\n"
            "ANTWORT:\n"
        )

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
