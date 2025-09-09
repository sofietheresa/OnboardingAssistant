interface Voice {
  name: string;
  language: string;
  gender: string;
  description: string;
}

interface TextToSpeechRequest {
  text: string;
  voice: string;
}

class TextToSpeechService {
  private baseUrl: string;
  private audioContext: AudioContext | null = null;
  private currentAudio: HTMLAudioElement | null = null;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  }

  async synthesizeText(text: string, voice: string = "de-DE_BirgitVoice"): Promise<string> {
    try {
      const request: TextToSpeechRequest = {
        text: text,
        voice: voice
      };

      const response = await fetch(`${this.baseUrl}/api/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = 'Text to Speech Fehler';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Falls JSON-Parsing fehlschlägt, verwende Standard-Fehlermeldung
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      // Audio-Daten als Blob URL zurückgeben
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      return audioUrl;
    } catch (error) {
      console.error('Text to Speech Fehler:', error);
      throw new Error(`Sprachsynthese fehlgeschlagen: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
    }
  }

  async playText(text: string, voice: string = "de-DE_BirgitVoice"): Promise<void> {
    try {
      // Stoppe aktuell laufende Wiedergabe
      this.stopPlayback();

      // Synthetisiere Text zu Audio
      const audioUrl = await this.synthesizeText(text, voice);
      
      // Erstelle Audio-Element und spiele ab
      this.currentAudio = new Audio(audioUrl);
      
      return new Promise((resolve, reject) => {
        if (!this.currentAudio) return;

        this.currentAudio.onended = () => {
          this.cleanup();
          resolve();
        };

        this.currentAudio.onerror = (error) => {
          this.cleanup();
          reject(new Error('Fehler bei der Audio-Wiedergabe'));
        };

        this.currentAudio.play().catch(reject);
      });
    } catch (error) {
      console.error('Playback Fehler:', error);
      throw error;
    }
  }

  stopPlayback(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.cleanup();
    }
  }

  private cleanup(): void {
    if (this.currentAudio) {
      // Cleanup der Blob URL
      URL.revokeObjectURL(this.currentAudio.src);
      this.currentAudio = null;
    }
  }

  async getAvailableVoices(): Promise<Voice[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/text-to-speech/voices`);
      
      if (!response.ok) {
        let errorMessage = 'Fehler beim Abrufen der Stimmen';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return data.voices || [];
    } catch (error) {
      console.error('Fehler beim Abrufen der Stimmen:', error);
      return [];
    }
  }

  isPlaying(): boolean {
    return this.currentAudio !== null && !this.currentAudio.paused;
  }
}

export const textToSpeechService = new TextToSpeechService();


