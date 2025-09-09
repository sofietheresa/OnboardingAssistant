import os
import io
from typing import Optional
from fastapi import HTTPException
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from .config import settings

class TextToSpeechService:
    def __init__(self):
        # Watson Text to Speech Konfiguration
        # Verwende separaten API Key für Text to Speech oder fallback auf WATSONX_API_KEY
        self.api_key = settings.text_to_speech_api_key or settings.watsonx_api_key
        self.service_url = settings.text_to_speech_url
        
        # Prüfe ob API Key gültig ist (nicht Platzhalter)
        if not self.api_key or self.api_key == "your_text_to_speech_api_key_here":
            if settings.watsonx_api_key and settings.watsonx_api_key != "your_watsonx_api_key_here":
                self.api_key = settings.watsonx_api_key
            else:
                raise ValueError("TEXT_TO_SPEECH_API_KEY oder WATSONX_API_KEY environment variable is required")
        
        # Authenticator und Service initialisieren
        authenticator = IAMAuthenticator(self.api_key)
        self.text_to_speech = TextToSpeechV1(authenticator=authenticator)
        self.text_to_speech.set_service_url(self.service_url)
    
    async def synthesize_text(self, text: str, voice: str = "de-DE_BirgitVoice") -> bytes:
        """
        Synthetisiert Text zu Audio mit Watson Text to Speech
        """
        try:
            # Text-Validierung
            if not text or not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Text darf nicht leer sein"
                )
            
            if len(text) > 5000:  # Watson TTS Limit
                raise HTTPException(
                    status_code=400,
                    detail="Text ist zu lang. Maximum 5000 Zeichen erlaubt."
                )
            
            # Watson Text to Speech API aufrufen
            response = self.text_to_speech.synthesize(
                text=text,
                voice=voice,
                accept='audio/wav'
            ).get_result()
            
            # Audio-Daten als Bytes zurückgeben
            return response.content
            
        except HTTPException:
            # Re-raise HTTPExceptions unverändert
            raise
        except Exception as e:
            print(f"Text to Speech Fehler: {str(e)}")
            # Spezifische Fehlermeldungen für häufige Probleme
            if "authentication" in str(e).lower():
                raise HTTPException(
                    status_code=401, 
                    detail="Authentifizierung fehlgeschlagen. Bitte überprüfen Sie die API-Konfiguration."
                )
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                raise HTTPException(
                    status_code=503, 
                    detail="Verbindung zum Text-to-Speech Service fehlgeschlagen. Bitte versuchen Sie es später erneut."
                )
            elif "voice" in str(e).lower():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Stimme '{voice}' nicht verfügbar. Bitte wählen Sie eine andere Stimme."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Fehler bei der Sprachsynthese: {str(e)}"
                )
    
    def get_available_voices(self) -> list:
        """
        Gibt verfügbare deutsche Stimmen zurück
        """
        try:
            voices = self.text_to_speech.list_voices().get_result()
            german_voices = []
            
            for voice in voices['voices']:
                if voice['language'].startswith('de-'):
                    german_voices.append({
                        'name': voice['name'],
                        'language': voice['language'],
                        'gender': voice['gender'],
                        'description': voice['description']
                    })
            
            return german_voices
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Stimmen: {str(e)}")
            return []

# Globale Instanz des Services
text_to_speech_service: Optional[TextToSpeechService] = None

def get_text_to_speech_service() -> TextToSpeechService:
    """Singleton-Pattern für den Text to Speech Service"""
    global text_to_speech_service
    if text_to_speech_service is None:
        try:
            text_to_speech_service = TextToSpeechService()
        except ValueError as e:
            print(f"Text to Speech Service konnte nicht initialisiert werden: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Text to Speech Service ist nicht konfiguriert"
            )
    return text_to_speech_service

