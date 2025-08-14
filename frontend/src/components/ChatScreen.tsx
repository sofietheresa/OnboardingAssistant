import React, { useState, useRef, useEffect } from 'react';
import { ChatScreenProps } from '../types';

const ChatScreen: React.FC<ChatScreenProps> = ({
  location,
  messages,
  onSendMessage,
  onBackToOnboarding,
  isLoading
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('de-DE', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-screen">
      <div className="chat-header">
        <div className="chat-header-left">
          <button className="back-button" onClick={onBackToOnboarding}>
            ← Zurück
          </button>
          <div className="location-info">
            <h2>{location.name}</h2>
            <p>{location.description}</p>
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user' : 'assistant'}`}
          >
            <div className="message-content">
              {message.text}
              <div style={{ 
                fontSize: '0.8rem', 
                opacity: 0.7, 
                marginTop: '5px',
                textAlign: message.isUser ? 'right' : 'left'
              }}>
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            Boardy schreibt...
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <div className="input-container">
          <input
            type="text"
            className="message-input"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Schreiben Sie eine Nachricht..."
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!inputText.trim() || isLoading}
          >
            Senden
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatScreen; 