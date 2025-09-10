from typing import List, Dict
from pgvector import Vector
from .embeddings import get_watsonx_ai_embeddings
from .db import get_conn

SYSTEM_PROMPT = (
    # Boardy – Onboarding-Assistent

    ## Rolle
    Du bist **Boardy**, der Onboarding-Assistent für neue Mitarbeitende bei IBM Böblingen, IBM München und der UDG Ludwigsburg.  
    Du begleitest sie freundlich, kompetent, empathisch und hilfreich.  

    ## Regeln
    - Nutze nur RAG-Dokumente, passend zur Lokation.  
    - Sprich die Nutzer:innen mit **„du“** an, locker aber professionell.  
    - Antworte **immer auf Deutsch**.  
    - Ergänze, wenn sinnvoll, kurze Tipps oder Zusatzinfos.  
    - Vermeide Geschwätzigkeit, bleibe klar und hilfreich.  
    - Berücksichtige den bisherigen Gesprächskontext.  

    ## Antwortformat (immer gleich)
    Antwort: <klare, hilfreiche Antwort>
    Quelle: <Dokument/Link>/nichts
    Tipp: <ergänzende Info oder kleiner Hinweis>
    Rückfrage: <lockere Rückfrage zur Gesprächsatmosphäre>

    ## Fallbacks
    - **Unsicherheit:**  
    `Antwort: Da bin ich mir nicht sicher, aber ich kann dir die richtige Ansprechperson nennen.`  

    - **Keine Infos:**  
    `Antwort: Das weiß ich leider nicht. Bitte teile mir die Info oder ein Dokument, dann nehme ich es ins RAG auf.`  

    ## Gesprächsabschluss
    (abwechselnd, ohne „Antwort:“ davor)  
    - „War meine Antwort für dich hilfreich?“  
    - „Gibt es noch etwas, wobei ich dich unterstützen kann?“  

    ## Ziel
    Neue Mitarbeitende sollen sich willkommen, ernst genommen und unterstützt fühlen.  
    Boardy ist Wissensquelle **und** persönliche Begleitung.  
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
    """Retrieve relevant documents from database using embeddings"""
    try:
        embedder = get_watsonx_ai_embeddings()
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
    except Exception as e:
        # Fallback: return empty list if embeddings or database fails
        print(f"Warning: RAG retrieval failed: {e}")
        return []

def is_smalltalk(question: str) -> bool:
    """
    Erkennt Smalltalk-Fragen basierend auf Kontext und Frageart, nicht nur Keywords.
    """
    question_lower = question.lower().strip()
    words = question_lower.split()
    
    # 1. Sehr kurze Fragen (1-2 Wörter) sind meist Smalltalk
    if len(words) <= 2:
        # Ausnahme: W-Fragen können fachlich sein
        w_questions = ["was", "wie", "wo", "wann", "warum", "wer", "welche", "welcher"]
        if not any(word in words for word in w_questions):
            return True
    
    # 2. Begrüßungen und Verabschiedungen
    greetings = ["hallo", "hi", "hey", "guten", "servus", "moin", "tschüss", "bye", "auf wiedersehen", "ciao"]
    if any(greeting in question_lower for greeting in greetings):
        return True
    
    # 3. Persönliche Fragen über den Assistenten
    personal_questions = [
        "wer bist", "was bist", "wie heißt", "woher kommst", "wie alt", 
        "wo wohnst", "hast du", "magst du", "kannst du", "bist du"
    ]
    if any(pq in question_lower for pq in personal_questions):
        return True
    
    # 4. Emotionale/soziale Fragen
    emotional_indicators = [
        "wie geht", "wie gehts", "was machst", "was machst du", "danke", "bitte",
        "lustig", "witzig", "spaß", "langweilig", "müde", "hungrig", "durstig", "krank"
    ]
    if any(ei in question_lower for ei in emotional_indicators):
        return True
    
    # 5. Wetter und allgemeine Themen
    general_topics = [
        "wetter", "regen", "sonne", "schön", "schlecht", "wochenende", "urlaub", "feiern", "party"
    ]
    if any(gt in question_lower for gt in general_topics):
        return True
    
    # 6. Fragen ohne fachlichen Kontext (keine Onboarding-relevanten Begriffe)
    onboarding_keywords = [
        "onboarding", "einstieg", "erste", "woche", "tag", "arbeit", "projekt", "team", "kollegen",
        "hr", "personal", "urlaub", "kantine", "essen", "parken", "parkplatz", "it", "computer",
        "laptop", "sicherheit", "schulung", "training", "lernen", "gehalt", "lohn", "bezahlung",
        "vertrag", "arbeitsplatz", "büro", "meeting", "termin", "deadline", "kunde", "client",
        "prozess", "workflow", "tool", "software", "system", "zugang", "berechtigung", "recht"
    ]
    
    # Wenn keine Onboarding-relevanten Begriffe enthalten sind, ist es wahrscheinlich Smalltalk
    if not any(keyword in question_lower for keyword in onboarding_keywords):
        # Aber nur wenn es nicht eine echte Frage ist
        question_indicators = ["was", "wie", "wo", "wann", "warum", "wer", "welche", "welcher", "kann", "soll", "muss"]
        if not any(indicator in question_lower for indicator in question_indicators):
            return True
    
    # 7. Sehr allgemeine Fragen ohne spezifischen Kontext
    if len(words) <= 4 and not any(keyword in question_lower for keyword in onboarding_keywords):
        return True
    
    return False

def generate_simple_response(question: str, contexts: List[Dict] = None, location: Dict = None, chat_history: List[Dict] = None) -> str:
    """Generate a simple response based on question and context"""
    question_lower = question.lower().strip()
    
    # Build location context
    location_context = ""
    if location:
        location_context = f" (Standort: {location.get('name', 'unbekannt')})"
    
    # Build chat history context
    chat_context = ""
    if chat_history and len(chat_history) > 0:
        # Take last 3 messages for context
        recent_messages = chat_history[-3:]
        chat_context = "\n\nBisheriger Gesprächsverlauf:\n"
        for msg in recent_messages:
            # Use generic labels instead of hardcoded names
            speaker = "User" if msg.get('isUser', False) else "Assistant"
            chat_context += f"{speaker}: {msg.get('text', '')}\n"
    
    # Smalltalk responses
    if is_smalltalk(question):
        if any(greeting in question_lower for greeting in ["hallo", "hi", "hey", "guten"]):
            return f"Hallo! Ich bin dein Onboarding-Assistent{location_context}. Wie kann ich dir heute helfen?{chat_context}"
        elif "wie geht" in question_lower:
            return f"Mir geht es gut, danke der Nachfrage! Ich bin bereit, dir bei deinem Onboarding{location_context} zu helfen.{chat_context}"
        elif "danke" in question_lower:
            return f"Gerne geschehen! Gibt es noch etwas, wobei ich dir helfen kann?{chat_context}"
        elif any(bye in question_lower for bye in ["tschüss", "bye", "auf wiedersehen"]):
            return f"Auf Wiedersehen! Falls du noch Fragen hast, bin ich immer für dich da.{chat_context}"
        else:
            return f"Das ist eine interessante Frage! Ich bin hier, um dir beim Onboarding{location_context} zu helfen.{chat_context}"
    
    # Professional responses
    if contexts and len(contexts) > 0:
        # Build response with context
        context_info = []
        for c in contexts[:3]:  # Limit to top 3 contexts
            title = c["metadata"].get("filename") or c["doc_id"]
            context_info.append(f"[{title}#{c['chunk_id']}]")
        
        sources_text = ", ".join(context_info)
        
        return f"""Antwort: Basierend auf den verfügbaren Informationen{location_context} kann ich dir folgendes sagen: {question} - Die relevanten Details findest du in den bereitgestellten Dokumenten.
Quelle: {sources_text}
Tipp: Bei weiteren Fragen wende dich gerne an deinen Vorgesetzten oder die HR-Abteilung.
Rückfrage: War meine Antwort für dich hilfreich?{chat_context}"""
    
    # Fallback for no context
    return f"""Antwort: Das ist eine interessante Frage: '{question}'{location_context}. Leider kann ich in der aktuellen Version keine detaillierte Antwort geben.
Quelle: nichts
Tipp: Ich empfehle dir, dich an deinen Vorgesetzten, die HR-Abteilung oder deinen Mentor zu wenden.
Rückfrage: Gibt es noch etwas, wobei ich dich unterstützen kann?{chat_context}"""

async def answer(question: str, location: Dict = None, chat_history: List[Dict] = None) -> Dict:
    """Answer questions using RAG with local embeddings"""
    
    # Prüfe ob es sich um Smalltalk handelt
    if is_smalltalk(question):
        # Für Smalltalk: Einfache Antwort ohne Kontext
        output = generate_simple_response(question, location=location, chat_history=chat_history)
        return {"answer": output, "sources": []}
    
    # Normale fachliche Antwort mit Kontextsuche
    contexts = await retrieve(question, k=6)
    
    if contexts:
        # Wenn relevante Dokumente gefunden wurden, verwende RAG
        output = generate_simple_response(question, contexts, location=location, chat_history=chat_history)
        
        sources = [
            {
                "title": c["metadata"].get("filename") or c["doc_id"],
                "doc_id": c["doc_id"],
                "chunk_id": c["chunk_id"],
            }
            for c in contexts
        ]
        return {"answer": output, "sources": sources}
    else:
        # Fallback: Einfache Antwort ohne Kontext
        output = generate_simple_response(question, location=location, chat_history=chat_history)
        return {"answer": output, "sources": []}
