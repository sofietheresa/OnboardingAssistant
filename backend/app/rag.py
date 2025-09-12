from typing import List, Dict
import logging
from pgvector import Vector
from .embeddings import WatsonxAIEmbeddings
from .llm import WatsonxAILLM
from .db import get_conn

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Du bist Boardy, ein freundlicher Onboarding-Assistent der Firma. "
    "Du kannst sowohl Smalltalk führen als auch fachliche Fragen beantworten. "
    "Antworte kurz, korrekt und freundlich auf Deutsch. "
    "Bei fachlichen Fragen nutze ausschließlich die bereitgestellten Kontexte. "
    "Bei Smalltalk oder allgemeinen Fragen antworte natürlich und hilfsbereit. "
    "Wenn du unsicher bist, sage dies klar und schlage einen Eskalationsweg vor. "
    "Bei fachlichen Antworten nenne immer die Quellen (Titel#Chunk)."
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
    logger.info(f"Retrieving for: '{query}'")
    
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
            logger.info(f"Found {len(rows)} documents")
            # Konvertiere Tuples zu Dicts
            return [dict(row) for row in rows]

def is_smalltalk(question: str) -> bool:
    """
    Erkennt Smalltalk-Fragen basierend auf Schlüsselwörtern und Mustern.
    """
    smalltalk_keywords = [
        "hallo", "hi", "hey", "guten tag", "guten morgen", "guten abend",
        "wie geht", "wie gehts", "was machst", "was machst du",
        "danke", "bitte", "tschüss", "auf wiedersehen", "bye",
        "wie heißt", "wer bist", "was bist", "woher kommst",
        "schönes wetter", "schlecht wetter", "regen", "sonne",
        "wie alt", "wo wohnst", "hast du", "magst du",
        "lustig", "witzig", "spaß", "langweilig",
        "müde", "hungrig", "durstig", "krank",
        "wochenende", "urlaub", "feiern", "party"
    ]
    
    question_lower = question.lower().strip()
    
    # Prüfe auf direkte Smalltalk-Keywords
    for keyword in smalltalk_keywords:
        if keyword in question_lower:
            return True
    
    # Prüfe auf sehr kurze Fragen (oft Smalltalk)
    if len(question_lower.split()) <= 2 and not any(word in question_lower for word in ["was", "wie", "wo", "wann", "warum", "wer"]):
        return True
    
    # Prüfe auf Begrüßungen
    if any(greeting in question_lower for greeting in ["hallo", "hi", "hey", "guten"]):
        return True
    
    return False

async def answer(question: str) -> Dict:
    # Prüfe ob es sich um Smalltalk handelt
    if is_smalltalk(question):
        # Für Smalltalk keine Kontextsuche, direkte Antwort
        llm = WatsonxAILLM()
        smalltalk_prompt = f"Du bist Boardy, ein freundlicher Onboarding-Assistent. Antworte auf diese Smalltalk-Frage natürlich und hilfsbereit auf Deutsch: {question}"
        output = await llm.generate(SYSTEM_PROMPT, smalltalk_prompt)
        return {"answer": output, "sources": []}
    
    # Normale fachliche Antwort mit Kontextsuche
    contexts = await retrieve(question, k=6)
    prompt = format_prompt(question, contexts)

    llm = WatsonxAILLM()
    output = await llm.generate(SYSTEM_PROMPT, prompt)

    logger.info(f"Output: {output}")

    sources = [
        {
            "title": c["metadata"].get("filename") or c["doc_id"],
            "doc_id": c["doc_id"],
            "chunk_id": c["chunk_id"],
        }
        for c in contexts
    ]
    logger.info(f"Created {len(sources)} sources")
    return {"answer": output, "sources": sources}
