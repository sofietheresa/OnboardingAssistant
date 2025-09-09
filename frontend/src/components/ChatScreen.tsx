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
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Erstelle Audio-Blob mit korrektem Format für Watson
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setIsRecording(false);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        
        // Audio direkt senden
        await sendAudioMessage(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Mikrofon konnte nicht aktiviert werden. Bitte überprüfen Sie die Berechtigungen.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const sendAudioMessage = async (audioBlob: Blob) => {
    try {
      // Transkribiere Audio zu Text
      const transcript = await speechToTextService.transcribeAudio(audioBlob);
      
      if (transcript.trim()) {
        // Sende die transkribierte Nachricht direkt
        onSendMessage(transcript);
      } else {
        alert('Keine Sprache erkannt. Bitte versuchen Sie es erneut.');
      }
    } catch (error) {
      console.error('Audio-Verarbeitung fehlgeschlagen:', error);
      alert(`Audio-Verarbeitung fehlgeschlagen: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() && !selectedFile && !audioBlob) return;
    
    const fileAttachment = selectedFile ? {
      name: selectedFile.name,
      size: selectedFile.size,
      type: selectedFile.type,
      url: URL.createObjectURL(selectedFile)
    } : undefined;

    const audioAttachment = audioBlob ? {
      name: 'Sprachaufnahme.wav',
      size: audioBlob.size,
      type: audioBlob.type,
      url: URL.createObjectURL(audioBlob)
    } : undefined;
    
    const messageText = inputValue.trim() || (audioBlob ? '🎤 Sprachaufnahme gesendet' : '');
    onSendMessage(messageText, fileAttachment || audioAttachment);
    
    setInputValue('');
    setSelectedFile(null);
    setAudioBlob(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
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

  const handleRemoveAudio = () => setAudioBlob(null);

  const handleVoiceClick = () => {
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

            {/* Audio Recording Display - Bottom Left */}
            {audioBlob && (
              <div className="selected-file-display audio-display">
                <div className="file-info">
                  <span className="file-name" title="Sprachaufnahme">
                    🎤 Sprachaufnahme
                  </span>
                  <button 
                    type="button" 
                    onClick={handleRemoveAudio} 
                    className="remove-file-x"
                    aria-label="Sprachaufnahme entfernen"
                  >
                    ×
                  </button>
                </div>
              </div>
            )}


            {/* Conditional buttons based on input */}
            {inputValue.trim() || selectedFile || audioBlob ? (
              /* Send Button - Arrow pointing up */
              <button className="send-button" onClick={handleSubmit}>
                <div className="send-arrow">↑</div>
              </button>
            ) : (
              <>
                {/* Voice Button with Microphone Icon */}
                <button 
                  className={`microphone-button ${isRecording ? 'recording' : ''}`} 
                  onClick={handleVoiceClick}
                  title={
                    isRecording 
                      ? 'Aufnahme stoppen (Klicken zum Stoppen)' 
                      : 'Sprachaufnahme starten (Klicken zum Starten)'
                  }
                  aria-label={
                    isRecording 
                      ? 'Aufnahme läuft - Klicken zum Stoppen' 
                      : 'Sprachaufnahme starten'
                  }
                >
                  <img 
                    src="/microphone.svg" 
                    alt={isRecording ? "Aufnahme läuft" : "Voice Input"} 
                    className="microphone-icon"
                  />
                  {isRecording && <div className="recording-indicator"></div>}
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
