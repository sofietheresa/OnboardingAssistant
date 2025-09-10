from typing import List, Dict
import logging
from pgvector import Vector
from .embeddings import get_watsonx_ai_embeddings
from .db import get_conn

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
    # Boardy – Onboarding-Assistent

    ## Rolle
    Du bist **Boardy**, der Onboarding-Assistent für neue Mitarbeitende bei IBM Böblingen, IBM München und der UDG Ludwigsburg.  
    Du begleitest sie freundlich, kompetent, empathisch und hilfreich.  

    ## Regeln
    - Nutze nur RAG-Dokumente, passend zur Lokation.  
- Sprich die Nutzer:innen mit **"du"** an, locker aber professionell.  
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
(abwechselnd, ohne "Antwort:" davor)  
- "War meine Antwort für dich hilfreich?"  
- "Gibt es noch etwas, wobei ich dich unterstützen kann?"  

    ## Ziel
    Neue Mitarbeitende sollen sich willkommen, ernst genommen und unterstützt fühlen.  
    Boardy ist Wissensquelle **und** persönliche Begleitung.  
"""


async def get_relevant_documents(query: str, location = None, limit: int = 5) -> List[Dict]:
    """
    Retrieves relevant documents from the database based on the query.
    
    Args:
        query: The user's question
        location: Optional location filter (Böblingen, München, UDG)
        limit: Maximum number of documents to return
    
    Returns:
        List of relevant documents with metadata
    """
    try:
        # Get query embedding
        embeddings_service = get_watsonx_ai_embeddings()
        try:
            query_embedding = await embeddings_service.embed([query])
            query_embedding = query_embedding[0]
        except Exception as embed_error:
            logger.error(f"Embeddings failed: {embed_error}")
            # Return empty list if embeddings fail
            return []
        
        # Convert to pgvector format
        query_vector = Vector(query_embedding)
        
        conn = get_conn()
        cursor = conn.cursor()
        
        # Build location filter
        location_filter = ""
        if location:
            location_filter = f"AND location = '{location}'"
        
        # Query for similar documents
        query_sql = f"""
        SELECT 
            id,
            content,
            metadata,
            location,
            source,
            created_at,
            embedding <-> %s AS distance
        FROM documents
        WHERE 1=1 {location_filter}
        ORDER BY embedding <-> %s
        LIMIT %s
        """
        
        cursor.execute(query_sql, (query_vector, query_vector, limit))
        results = cursor.fetchall()
        
        documents = []
        for row in results:
            documents.append({
                'id': row[0],
                'content': row[1],
                'metadata': row[2],
                'location': row[3],
                'source': row[4],
                'created_at': row[5],
                'distance': float(row[6])
            })
        
        cursor.close()
        conn.close()
        
        return documents
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        return []


def format_context(documents: List[Dict]) -> str:
    """
    Formats the retrieved documents into a context string for the LLM.
    
    Args:
        documents: List of relevant documents
    
    Returns:
        Formatted context string
    """
    if not documents:
        return "Keine relevanten Dokumente gefunden."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(f"""
Dokument {i}:
Quelle: {doc.get('source', 'Unbekannt')}
Standort: {doc.get('location', 'Unbekannt')}
Inhalt: {doc['content'][:500]}{'...' if len(doc['content']) > 500 else ''}
""")
    
    return "\n".join(context_parts)


async def answer(question: str, location = None, conversation_history: List[Dict] = None) -> Dict:
    """
    Generates an answer using RAG (Retrieval-Augmented Generation).
    
    Args:
        question: The user's question
        location: Optional location filter
        conversation_history: Previous conversation messages
    
    Returns:
        Dictionary containing the answer and metadata
    """
    try:
        # Extract location ID if location is an object
        location_id = None
        if location:
            if isinstance(location, dict):
                location_id = location.get('id')
            else:
                location_id = location
        
        # Get relevant documents
        documents = await get_relevant_documents(question, location_id)
        
        # Check if we have any documents
        if not documents:
            return {
                "answer": "Entschuldigung, ich konnte keine relevanten Informationen zu deiner Frage finden. Bitte versuche es mit einer anderen Formulierung oder wende dich an einen Kollegen.",
                "sources": [],
                "context": "",
                "documents_found": 0
            }
        
        # Format context
        context = format_context(documents)
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            history_parts = []
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "Nutzer" if msg.get('role') == 'user' else "Boardy"
                history_parts.append(f"{role}: {msg.get('content', '')}")
            history_text = "\n".join(history_parts)
        
        # Create the prompt
        prompt = f"""
{SYSTEM_PROMPT}

## Kontext aus RAG-Dokumenten:
{context}

## Gesprächsverlauf:
{history_text if history_text else "Kein vorheriger Gesprächsverlauf."}

## Aktuelle Frage:
{question}

Bitte beantworte die Frage basierend auf den bereitgestellten Dokumenten und dem Gesprächskontext.
"""
        
        # For now, return a simple response
        # In a real implementation, this would call the LLM
        response = {
            "answer": f"Antwort: Ich habe deine Frage '{question}' erhalten und suche in den verfügbaren Dokumenten nach relevanten Informationen.",
            "sources": [doc.get('source', 'Unbekannt') for doc in documents],
            "context": context,
            "documents_found": len(documents)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in answer function: {str(e)}")
        return {
            "answer": "Entschuldigung, es ist ein technischer Fehler aufgetreten. Bitte versuche es später erneut oder wende dich an einen Administrator.",
            "sources": [],
            "context": "",
            "documents_found": 0
        }