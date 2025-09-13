from typing import List, Dict, Optional
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
        f"KONTEXT (verwende bevorzugt Folgendes, du darfst aber auch eigenes Wissen nutzen, wenn du dir sicher bist):\n{ctx}\n\n"
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

async def answer(question: str, extra_contexts: Optional[List[Dict]] = None, chat_history: Optional[List[Dict]] = None) -> Dict:
    # Wenn extra_contexts (z.B. aus Datei) übergeben werden, diese mit DB-Kontexten kombinieren
    db_contexts = await retrieve(question, k=6)
    contexts = db_contexts.copy()
    if extra_contexts:
        # Füge die extra Kontexte (z.B. aus Datei) hinten an, max 8 insgesamt
        contexts += extra_contexts
        contexts = contexts[:8]

    # Chatverlauf in den Prompt einbauen
    history_prompt = ""
    if chat_history:
        for turn in chat_history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role == "user":
                history_prompt += f"Nutzer: {content}\n"
            else:
                history_prompt += f"Assistent: {content}\n"

    if contexts:  # normaler RAG-Flow oder mit Datei-Kontext
        prompt = history_prompt + format_prompt(question, contexts)
    else:  # kein Kontext gefunden → fallback
        prompt = history_prompt + (
            f"FRAGE:\n{question}\n\n"
            "Es konnte kein relevanter Kontext gefunden werden. "
            "Antworte bitte trotzdem kurz, korrekt, auf Deutsch, "
            "auf Basis deines eigenen Wissens. "
            "Wenn du unsicher bist, sage dies klar und schlage einen Eskalationsweg vor.\n\n"
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
