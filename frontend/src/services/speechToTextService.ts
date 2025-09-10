interface SpeechToTextResponse {
  transcript: string;
  confidence: number;
}

interface SpeechToTextRequest {
  audio_data: string; // Base64-encoded audio data
  content_type: string;
}

class SpeechToTextService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  }

  async transcribeAudio(audioBlob: Blob): Promise<string> {
    try {
      // Audio-Blob zu Base64 konvertieren
      const base64Audio = await this.blobToBase64(audioBlob);
      
      const request: SpeechToTextRequest = {
        audio_data: base64Audio,
        content_type: audioBlob.type || 'audio/webm'
      };

      const response = await fetch(`${this.baseUrl}/api/speech-to-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = 'Speech to Text Fehler';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Falls JSON-Parsing fehlschlägt, verwende Standard-Fehlermeldung
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const result: SpeechToTextResponse = await response.json();
      return result.transcript;
    } catch (error) {
      console.error('Speech to Text Fehler:', error);
      throw new Error(`Spracherkennung fehlgeschlagen: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
    }
  }

  private async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Entferne den Data-URL-Prefix (data:audio/wav;base64,)
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }
}

export const speechToTextService = new SpeechToTextService();


