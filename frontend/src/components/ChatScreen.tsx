import React, { useState, useRef, useEffect } from 'react';
import { ChatScreenProps, Source } from '../types';
import { speechToTextService } from '../services/speechToTextService';
import { textToSpeechService } from '../services/textToSpeechService';
import '../styles/ChatScreen.css';

const ChatScreen: React.FC<ChatScreenProps> = ({ 
  location, 
  messages, 
  onSendMessage, 
  onBackToOnboarding, 
  isLoading 
}) => {
  const [inputValue, setInputValue] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playingMessageId, setPlayingMessageId] = useState<string | null>(null);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showIngestPrompt, setShowIngestPrompt] = useState(false);
  const [lastUploadedFilename, setLastUploadedFilename] = useState<string | null>(null);
  const [askWithFileMode, setAskWithFileMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cleanup function for MediaRecorder
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [isRecording]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,  // 16kHz für Watson Speech-to-Text
          channelCount: 1,    // Mono
          echoCancellation: false,
          noiseSuppression: false
        } 
      });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Timer für Aufnahmedauer
      let timer: ReturnType<typeof setInterval>;
      
      mediaRecorder.onstop = async () => {
        clearInterval(timer);
        
        // Erstelle Audio-Blob mit korrektem Format für Watson
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setIsRecording(false);
        setRecordingDuration(0);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        
        // Prüfe Mindestgröße der Audio-Daten
        if (audioBlob.size < 100) {
          alert(`Aufnahme zu kurz (${audioBlob.size} Bytes). Bitte sprechen Sie länger.`);
          return;
        }
        
        // Audio direkt senden
        await sendAudioMessage(audioBlob);
      };

      // Starte mit 100ms Intervallen für bessere Qualität
      mediaRecorder.start(100);
      setIsRecording(true);
      setRecordingDuration(0);
      
      // Timer für Aufnahmedauer starten
      timer = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Mikrofon konnte nicht aktiviert werden. Bitte überprüfen Sie die Berechtigungen.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      // Kleine Verzögerung, um sicherzustellen, dass alle Audio-Daten erfasst werden
      setTimeout(() => {
        if (mediaRecorderRef.current && isRecording) {
          mediaRecorderRef.current.stop();
        }
      }, 100);
    }
  };

  const sendAudioMessage = async (audioBlob: Blob) => {
    try {
      console.log('Audio-Blob Größe:', audioBlob.size, 'Bytes');
      console.log('Audio-Blob Typ:', audioBlob.type);
      
      // Prüfe Mindestgröße erneut
      if (audioBlob.size < 100) {
        alert(`Audio-Aufnahme zu kurz (${audioBlob.size} Bytes). Bitte sprechen Sie länger.`);
        return;
      }
      
      // Starte Transkription
      setIsTranscribing(true);
      
      // Transkribiere Audio zu Text
      const transcript = await speechToTextService.transcribeAudio(audioBlob);
      
      if (transcript.trim()) {
        // Setze den transkribierten Text in die Eingabezeile
        setInputValue(transcript);
        // Kein Audio-Blob speichern - nur Text verwenden
        console.log('Transkription erfolgreich:', transcript);
      } else {
        alert('Keine Sprache erkannt. Bitte versuchen Sie es erneut.');
      }
    } catch (error) {
      console.error('Audio-Verarbeitung fehlgeschlagen:', error);
      console.error('Fehler-Details:', error);
      
      // Spezifischere Fehlermeldungen
      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch')) {
          alert('Verbindung zum Server fehlgeschlagen. Bitte überprüfen Sie, ob das Backend läuft.');
        } else if (error.message.includes('Konfidenz') || error.message.includes('confidence')) {
          // Bei Konfidenz-Problemen trotzdem versuchen, den Text zu verwenden
          console.log('Konfidenz-Warnung, aber versuche trotzdem zu verwenden');
          // Keine Fehlermeldung anzeigen, da das Backend jetzt niedrigere Konfidenz akzeptiert
        } else if (error.message.includes('400')) {
          alert('Audio-Aufnahme zu kurz oder unverständlich. Bitte sprechen Sie länger und deutlicher.');
        } else {
          alert(`Audio-Verarbeitung fehlgeschlagen: ${error.message}`);
        }
      } else {
        alert('Audio-Verarbeitung fehlgeschlagen: Unbekannter Fehler');
      }
    } finally {
      // Transkription beendet
      setIsTranscribing(false);
    }
  };

  const playText = async (text: string, messageId: string) => {
    try {
      if (isPlaying) {
        textToSpeechService.stopPlayback();
        setIsPlaying(false);
        setPlayingMessageId(null);
        return;
      }

      setIsPlaying(true);
      setPlayingMessageId(messageId);
      
      await textToSpeechService.playText(text);
      
      setIsPlaying(false);
      setPlayingMessageId(null);
    } catch (error) {
      console.error('Text to Speech Fehler:', error);
      alert(`Audio-Wiedergabe fehlgeschlagen: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
      setIsPlaying(false);
      setPlayingMessageId(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() && !selectedFile) return;

    if (selectedFile) {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', selectedFile);
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
        const res = await fetch(`${apiUrl}/api/upload-file`, {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        if (data.success) {
          setLastUploadedFilename(data.filename);
          setShowIngestPrompt(true);
        } else {
          alert('Dateiupload fehlgeschlagen.');
        }
      } catch (err) {
        alert('Fehler beim Upload.');
      } finally {
        setUploading(false);
      }
      return;
    }

    // Nur Textnachricht senden
    const messageText = inputValue.trim();
    onSendMessage(messageText);
    setInputValue('');
  };

  const handleIngestConfirm = async () => {
    if (!lastUploadedFilename) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('filename', lastUploadedFilename);
    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
      const res = await fetch(`${apiUrl}/api/ingest-uploaded-file`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.ingested) {
        alert('Datei wurde ins RAG aufgenommen.');
      } else {
        alert('Ingest fehlgeschlagen.');
      }
    } catch (err) {
      alert('Fehler beim Ingest.');
    } finally {
      setShowIngestPrompt(false);
      setUploading(false);
      setSelectedFile(null);
      setInputValue('');
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleIngestCancel = () => {
    setShowIngestPrompt(false);
    setAskWithFileMode(true);
    // Datei bleibt ausgewählt, damit sie für Fragen verwendet werden kann
  };

const handleAskWithFile = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!inputValue.trim() || !selectedFile) return;
  setUploading(true);

  const formData = new FormData();
  formData.append('query', inputValue.trim());
  formData.append('file', selectedFile);

  try {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
    const res = await fetch(`${apiUrl}/api/ask-with-file`, {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();

    if (data.answer) {
      // User-Frage direkt ins Messages-Array schreiben
      setMessages(prev => [
        ...prev,
        {
          id: crypto.randomUUID(),
          text: inputValue.trim(),
          isUser: true,
          timestamp: new Date(),
          fileAttachment: {
            name: selectedFile.name,
            size: selectedFile.size,
            type: selectedFile.type,
            url: URL.createObjectURL(selectedFile),
          }
        },
        {
          id: crypto.randomUUID(),
          text: data.answer,
          isUser: false,
          timestamp: new Date(),
          sources: data.sources || []
        }
      ]);
    } else {
      alert('Keine Antwort erhalten.');
    }
  } catch (err) {
    alert('Fehler bei der Anfrage mit Datei.');
  } finally {
    setUploading(false);
    setAskWithFileMode(false);
    setSelectedFile(null);
    setInputValue('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }
};


  const handlePlusClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) setSelectedFile(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // handleRemoveAudio entfernt - wird nicht mehr benötigt

  const handleVoiceClick = () => {
    // Verhindere Klicks während der Transkription
    if (isTranscribing) {
      return;
    }
    
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const formatMessageWithSources = (text: string, sources?: Source[]) => {
    // Extrahiere nur den Text zwischen "ANTWORT:" und dem nächsten Schlüsselwort
    const extractAnswer = (fullText: string) => {
      // Entferne zuerst alle "Quellen:"-Teile am Ende
      let cleanText = fullText.replace(/\n?\s*Quellen:?\s*.*$/s, '').trim();
      
      // Suche nach "ANTWORT:" und extrahiere Text
      const answerMatch = cleanText.match(/ANTWORT:?\s*(.*)/s);
      
      if (answerMatch) {
        let answerText = answerMatch[1].trim();
        
        // Entferne weitere Schlüsselwörter am Ende
        answerText = answerText.replace(/\n?\s*(?:Quellen|Quelle|Sources|Source|FRAGE|Frage|KONTEXT|Kontext|HINWEIS|Hinweis):\s*.*$/s, '').trim();
        
        // Entferne Markdown-Formatierung
        answerText = answerText.replace(/^\s*[-*]\s*/gm, ''); // Listenzeichen
        answerText = answerText.replace(/\*\*(.*?)\*\*/g, '$1'); // Fett-Formatierung
        answerText = answerText.replace(/\*(.*?)\*/g, '$1'); // Kursiv-Formatierung
        answerText = answerText.replace(/`(.*?)`/g, '$1'); // Code-Formatierung
        answerText = answerText.replace(/#{1,6}\s*/g, ''); // Überschriften
        answerText = answerText.replace(/\n{3,}/g, '\n\n'); // Mehrfache Zeilenumbrüche
        
        return answerText.trim();
      }
      
      // Fallback: Falls kein "ANTWORT:" gefunden wird, gib den gesamten Text zurück
      return cleanText.trim();
    };

    const answerText = extractAnswer(text);

    if (!sources || sources.length === 0) {
      return <span>{answerText}</span>;
    }

    // Entferne Duplikate basierend auf doc_id und title
    const uniqueSources = sources.filter((source, index, self) => 
      index === self.findIndex(s => s.doc_id === source.doc_id && s.title === source.title)
    );

    // Erstelle Quellen-Buttons
    const sourceButtons = uniqueSources.map((source, index) => (
      <button
        key={`${source.doc_id}-${source.chunk_id}-${index}`}
        className="source-button"
        onClick={() => {
          // Hier könntest du eine Funktion hinzufügen, um die Quelle zu öffnen
          console.log('Quelle geöffnet:', source);
        }}
        title={`Quelle: ${source.title}`}
      >
        {source.title}
      </button>
    ));

    return (
      <div className="message-with-sources">
        <span className="answer-text">{answerText}</span>
        <div className="sources-container">
          {sourceButtons}
        </div>
      </div>
    );
  };

  if (showIngestPrompt) {
    return (
      <div className="ingest-prompt-modal">
        <div className="ingest-prompt-content">
          <p>Möchtest du die Datei <b>{lastUploadedFilename}</b> ins RAG aufnehmen?</p>
          <button onClick={handleIngestConfirm} disabled={uploading}>Ja, aufnehmen</button>
          <button onClick={handleIngestCancel} disabled={uploading}>Nein</button>
        </div>
      </div>
    );
  }

  if (askWithFileMode) {
    return (
      <div className="ask-with-file-modal">
        <div className="ask-with-file-content">
          <p>Stelle eine Frage zu <b>{selectedFile?.name}</b> (ohne Ingest ins RAG):</p>
          <form onSubmit={handleAskWithFile}>
            <textarea
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              placeholder="Deine Frage zum Dokument..."
              className="message-input"
              rows={2}
              autoFocus
            />
            <button type="submit" disabled={uploading || !inputValue.trim()}>Frage stellen</button>
            <button type="button" onClick={() => { setAskWithFileMode(false); setSelectedFile(null); setInputValue(''); }} disabled={uploading}>Abbrechen</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-screen">
        {/* Header Section - Exact from Figma */}
        <div className="chat-header">
          {/* Left side: Arrow and Boardy */}
          <div className="header-left">
            {/* Yellow Arrow pointing left - Navigation */}
            <div className="yellow-arrow" onClick={onBackToOnboarding}>←</div>
            
            {/* Back Button with Boardy Robot */}
            <div className="back-button-container">
              <button className="back-button" onClick={onBackToOnboarding}>
                <img 
                  src="/boardy_small.svg" 
                  alt="Boardy Robot" 
                  className="boardy-icon"
                />
              </button>
            </div>
          </div>

          {/* Location Title (e.g., "UDG Ludwigsburg") */}
          <div className="location-title">
            {location.name}
          </div>
        </div>

        {/* Chat Messages Area */}
        <div className="chat-messages">
          {/* Initial Boardy Message - styled exactly like Figma */}
          <div className="message assistant">
            <div className="message-content">
              Wie kann ich dir helfen?
            </div>
          </div>

          {/* Additional messages */}
          {messages.slice(1).map((message) => (
            <div key={message.id} className={`message ${message.isUser ? 'user' : 'assistant'}`}>
              <div className="message-content">
                {message.isUser ? (
                  message.text
                ) : (
                  <div className="assistant-message">
                    <div className="message-text">
                      {formatMessageWithSources(message.text, message.sources)}
                    </div>
                    <button
                      className={`play-button ${playingMessageId === message.id ? 'playing' : ''}`}
                      onClick={() => playText(message.text, message.id)}
                      title={playingMessageId === message.id ? 'Audio stoppen' : 'Audio abspielen'}
                      aria-label={playingMessageId === message.id ? 'Audio stoppen' : 'Audio abspielen'}
                    >
                      {playingMessageId === message.id ? '⏸️' : '🔊'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="loading-indicator">
              <div className="typing-animation">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Section - Neuanordnung wie Screenshot */}
        <div className="chat-input-container">
          {/* Plus Button - Außerhalb der blauen Box, links */}
          <button className="plus-button-outside" onClick={handlePlusClick}>
            <span className="plus-icon">+</span>
          </button>

          {/* Light blue input background container */}
          <div className={`input-background ${selectedFile || audioBlob ? 'has-document' : ''}`}>
            {/* Hidden File Input */}
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              style={{ display: 'none' }} 
              accept="*/*"
            />

            {/* Text Input Form */}
            <form onSubmit={handleSubmit} className="chat-input-form">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Frag etwas!"
                className="message-input"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                onInput={(e) => {
                  // Automatische Höhenanpassung
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                }}
              />
            </form>

            {/* Selected File Display - Bottom Left */}
            {selectedFile && (
              <div className="selected-file-display">
                <div className="file-info">
                  <span className="file-name" title={selectedFile.name}>
                    {selectedFile.name}
                  </span>
                  <button 
                    type="button" 
                    onClick={handleRemoveFile} 
                    className="remove-file-x"
                    aria-label="Dokument entfernen"
                  >
                    ×
                  </button>
                </div>
              </div>
            )}

            {/* Audio Recording Display - Entfernt, da nur Text verwendet wird */}


            {/* Conditional buttons based on input */}
            {inputValue.trim() || selectedFile ? (
              /* Send Button - Arrow pointing up */
              <button className="send-button" onClick={handleSubmit}>
                <div className="send-arrow">↑</div>
              </button>
            ) : (
              <>
                {/* Voice Button with Microphone Icon or Loading Spinner */}
                <button 
                  className={`microphone-button ${isRecording ? 'recording' : ''} ${isTranscribing ? 'transcribing' : ''}`} 
                  onClick={handleVoiceClick}
                  disabled={isTranscribing}
                  title={
                    isTranscribing
                      ? 'Transkription läuft...'
                      : isRecording 
                        ? 'Aufnahme stoppen (Klicken zum Stoppen)' 
                        : 'Sprachaufnahme starten (Klicken zum Starten)'
                  }
                  aria-label={
                    isTranscribing
                      ? 'Transkription läuft - Bitte warten'
                      : isRecording 
                        ? 'Aufnahme läuft - Klicken zum Stoppen' 
                        : 'Sprachaufnahme starten'
                  }
                >
                  {isTranscribing ? (
                    <div className="loading-spinner"></div>
                  ) : (
                    <img 
                      src="/microphone.svg" 
                      alt={isRecording ? "Aufnahme läuft" : "Voice Input"} 
                      className="microphone-icon"
                    />
                  )}
                  {isRecording && (
                    <>
                      <div className="recording-indicator"></div>
                      <div className="recording-duration">{recordingDuration}s</div>
                    </>
                  )}
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
