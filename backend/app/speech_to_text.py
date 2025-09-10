import os
import io
from typing import Optional
from fastapi import HTTPException
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.websocket import RecognizeCallback
import json
from .config import settings

class SpeechToTextService:
    def __init__(self):
        # Watson Speech to Text Konfiguration
        # Verwende separaten API Key für Speech to Text oder fallback auf WATSONX_API_KEY
        self.api_key = settings.speech_to_text_api_key or settings.watsonx_api_key
        self.service_url = settings.speech_to_text_url
        
        # Prüfe ob API Key gültig ist (nicht Platzhalter)
        if not self.api_key or self.api_key == "your_speech_to_text_api_key_here":
            if settings.watsonx_api_key and settings.watsonx_api_key != "your_watsonx_api_key_here":
                self.api_key = settings.watsonx_api_key
            else:
                raise ValueError("SPEECH_TO_TEXT_API_KEY oder WATSONX_API_KEY environment variable is required")
        
        # Authenticator und Service initialisieren
        authenticator = IAMAuthenticator(self.api_key)
        self.speech_to_text = SpeechToTextV1(authenticator=authenticator)
        self.speech_to_text.set_service_url(self.service_url)
    
    async def transcribe_audio(self, audio_data: bytes, content_type: str = "audio/wav") -> str:
        """
        Transkribiert Audio-Daten zu Text mit Watson Speech to Text
        """
        try:
            # Watson Speech to Text unterstützt verschiedene Formate
            # Verwende das beste verfügbare Format basierend auf dem Input
            
            if content_type == 'audio/webm':
                watson_content_type = 'audio/webm'
            elif content_type == 'audio/wav':
                # Für WAV verwende audio/l16 mit 16kHz Sample Rate
                watson_content_type = 'audio/l16;rate=16000;channels=1'
            elif content_type == 'audio/mp4':
                watson_content_type = 'audio/mp4'
            elif content_type == 'audio/ogg':
                watson_content_type = 'audio/ogg;codecs=opus'
            else:
                # Fallback: Versuche es mit dem ursprünglichen Format
                watson_content_type = content_type
            
            print(f"Verwende Watson Content-Type: {watson_content_type}")
            
            response = self.speech_to_text.recognize(
                audio=audio_data,
                content_type=watson_content_type,
                model='de-DE_BroadbandModel'  # Deutsch-Modell
            ).get_result()
            
            # Text aus der Antwort extrahieren
            if response.get('results') and len(response['results']) > 0:
                transcript = response['results'][0]['alternatives'][0]['transcript']
                confidence = response['results'][0]['alternatives'][0].get('confidence', 0)
                
                # Akzeptiere Transkripte mit niedrigerer Konfidenz für bessere Benutzerfreundlichkeit
                if confidence > 0.1:  # Mindest-Konfidenz von 10%
                    return transcript.strip()
                else:
                    # Bei sehr niedriger Konfidenz trotzdem versuchen, aber mit Warnung
                    print(f"Warnung: Sehr niedrige Konfidenz ({confidence:.2f}), aber Transkript wird trotzdem zurückgegeben")
                    return transcript.strip()
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Keine Sprache erkannt. Bitte versuchen Sie es erneut."
                )
                
        except HTTPException:
            # Re-raise HTTPExceptions unverändert
            raise
        except Exception as e:
            print(f"Speech to Text Fehler: {str(e)}")
            # Spezifische Fehlermeldungen für häufige Probleme
            if "authentication" in str(e).lower():
                raise HTTPException(
                    status_code=401, 
                    detail="Authentifizierung fehlgeschlagen. Bitte überprüfen Sie die API-Konfiguration."
                )
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                raise HTTPException(
                    status_code=503, 
                    detail="Verbindung zum Speech-to-Text Service fehlgeschlagen. Bitte versuchen Sie es später erneut."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Fehler bei der Spracherkennung: {str(e)}"
                )

# Globale Instanz des Services
speech_to_text_service: Optional[SpeechToTextService] = None

def get_speech_to_text_service() -> SpeechToTextService:
    """Singleton-Pattern für den Speech to Text Service"""
    global speech_to_text_service
    if speech_to_text_service is None:
        try:
            speech_to_text_service = SpeechToTextService()
        except ValueError as e:
            print(f"Speech to Text Service konnte nicht initialisiert werden: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Speech to Text Service ist nicht konfiguriert"
            )
    return speech_to_text_service
