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
    logger.info(f"Starting document retrieval for query: '{query[:100]}...' with location: {location}, limit: {limit}")
    
    try:
        # Get query embedding
        logger.debug("Initializing embeddings service")
        embeddings_service = get_watsonx_ai_embeddings()
        try:
            logger.debug("Generating query embedding")
            query_embedding = await embeddings_service.embed([query])
            query_embedding = query_embedding[0]
            logger.debug(f"Query embedding generated successfully, dimension: {len(query_embedding)}")
        except Exception as embed_error:
            logger.error(f"Embeddings failed: {embed_error}")
            # Return empty list if embeddings fail
            return []
        
        # Convert to pgvector format
        logger.debug("Converting embedding to pgvector format")
        query_vector = Vector(query_embedding)
        
        logger.debug("Establishing database connection")
        conn = get_conn()
        cursor = conn.cursor()
        
        # Build location filter
        location_filter = ""
        if location:
            location_filter = f"AND location = '{location}'"
            logger.debug(f"Applied location filter: {location}")
        
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
        
        logger.debug(f"Executing similarity search with SQL: {query_sql}")
        cursor.execute(query_sql, (query_vector, query_vector, limit))
        results = cursor.fetchall()
        logger.info(f"Found {len(results)} documents from database")
        
        documents = []
        for i, row in enumerate(results):
            doc = {
                'id': row[0],
                'content': row[1],
                'metadata': row[2],
                'location': row[3],
                'source': row[4],
                'created_at': row[5],
                'distance': float(row[6])
            }
            documents.append(doc)
            logger.debug(f"Document {i+1}: ID={doc['id']}, source={doc['source']}, distance={doc['distance']:.4f}")
        
        cursor.close()
        conn.close()
        logger.info(f"Successfully retrieved {len(documents)} relevant documents")
        
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
    logger.debug(f"Formatting context from {len(documents)} documents")
    
    if not documents:
        logger.warning("No documents provided for context formatting")
        return "Keine relevanten Dokumente gefunden."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        content_preview = doc['content'][:500]
        truncated = len(doc['content']) > 500
        logger.debug(f"Document {i}: source={doc.get('source', 'Unbekannt')}, content_length={len(doc['content'])}, truncated={truncated}")
        
        context_parts.append(f"""
Dokument {i}:
Quelle: {doc.get('source', 'Unbekannt')}
Standort: {doc.get('location', 'Unbekannt')}
Inhalt: {content_preview}{'...' if truncated else ''}
""")
    
    formatted_context = "\n".join(context_parts)
    logger.debug(f"Context formatted successfully, total length: {len(formatted_context)} characters")
    
    return formatted_context


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
    logger.info(f"Starting RAG answer generation for question: '{question[:100]}...'")
    logger.debug(f"Location parameter: {location}")
    logger.debug(f"Conversation history length: {len(conversation_history) if conversation_history else 0}")
    
    try:
        # Extract location ID if location is an object
        location_id = None
        if location:
            if isinstance(location, dict):
                location_id = location.get('id')
                logger.debug(f"Extracted location ID from dict: {location_id}")
            else:
                location_id = location
                logger.debug(f"Using location as ID directly: {location_id}")
        
        # Get relevant documents
        logger.info("Retrieving relevant documents")
        documents = await get_relevant_documents(question, location_id)
        
        # Check if we have any documents
        if not documents:
            logger.warning("No relevant documents found for query")
            # Generate a helpful response even without documents
            return {
                "answer": f"Antwort: Hallo! Ich bin Boardy, dein Onboarding-Assistent. Gerne beantworte ich deine Frage: '{question}'\n\nDa ich noch keine spezifischen Dokumente zu diesem Thema in meiner Wissensdatenbank habe, kann ich dir eine allgemeine Antwort geben oder dich an die richtige Ansprechperson weiterleiten.\n\nTipp: Du kannst mir auch Dokumente hochladen, damit ich dir in Zukunft präzisere Antworten geben kann.\n\nRückfrage: Wie kann ich dir sonst noch beim Onboarding helfen?",
                "sources": [],
                "context": "Keine spezifischen Dokumente verfügbar - allgemeine Antwort basierend auf Systemwissen",
                "documents_found": 0
            }
        
        # Format context
        logger.info(f"Formatting context from {len(documents)} documents")
        context = format_context(documents)
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            logger.debug(f"Processing conversation history with {len(conversation_history)} messages")
            history_parts = []
            for i, msg in enumerate(conversation_history[-5:]):  # Last 5 messages
                role = "Nutzer" if msg.get('role') == 'user' else "Boardy"
                content = msg.get('content', '')
                history_parts.append(f"{role}: {content}")
                logger.debug(f"History message {i+1}: {role} - {content[:50]}...")
            history_text = "\n".join(history_parts)
            logger.debug(f"Formatted conversation history: {len(history_text)} characters")
        else:
            logger.debug("No conversation history provided")
        
        # Create the prompt
        logger.debug("Building prompt for LLM")
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
        logger.debug(f"Prompt created successfully, total length: {len(prompt)} characters")
        
        # Generate response based on available documents
        if documents:
            logger.info(f"Generating response with {len(documents)} documents")
            # With documents - provide specific information
            sources = [doc.get('source', 'Unbekannt') for doc in documents]
            logger.debug(f"Sources for response: {sources}")
            
            response = {
                "answer": f"Antwort: Basierend auf den verfügbaren Informationen kann ich dir folgendes zu deiner Frage '{question}' sagen:\n\n{context[:500]}{'...' if len(context) > 500 else ''}\n\nTipp: Die Informationen stammen aus {len(documents)} relevanten Dokument(en) in unserer Wissensdatenbank.\n\nRückfrage: Ist das die Information, die du gesucht hast?",
                "sources": sources,
                "context": context,
                "documents_found": len(documents)
            }
            logger.info(f"Response generated successfully with {len(documents)} documents")
        else:
            logger.warning("No documents available, generating fallback response")
            # Without documents - provide helpful general response
            response = {
                "answer": f"Antwort: Hallo! Ich bin Boardy, dein Onboarding-Assistent. Gerne beantworte ich deine Frage: '{question}'\n\nDa ich noch keine spezifischen Dokumente zu diesem Thema in meiner Wissensdatenbank habe, kann ich dir eine allgemeine Antwort geben oder dich an die richtige Ansprechperson weiterleiten.\n\nTipp: Du kannst mir auch Dokumente hochladen, damit ich dir in Zukunft präzisere Antworten geben kann.\n\nRückfrage: Wie kann ich dir sonst noch beim Onboarding helfen?",
                "sources": [],
                "context": "Keine spezifischen Dokumente verfügbar - allgemeine Antwort basierend auf Systemwissen",
                "documents_found": 0
            }
        
        logger.info("RAG answer generation completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in answer function: {str(e)}")
        return {
            "answer": "Entschuldigung, es ist ein technischer Fehler aufgetreten. Bitte versuche es später erneut oder wende dich an einen Administrator.",
            "sources": [],
            "context": "",
            "documents_found": 0
        }